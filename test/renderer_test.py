import sys
import numpy as np
import argparse

from tempfile import TemporaryDirectory


parser = argparse.ArgumentParser()
parser.add_argument(
    "--threshold",
    type=float,
    default=0.01,
    help="threshold to trigger event"
)
parser.add_argument(
    "--start",
    type=float,
    default=0.0,
    help="start point of video stream"
)
parser.add_argument(
    "--stop",
    type=float,
    default=5.0,
    help="stop point of video stream"
)
parser.add_argument(
    "--fname",
    type=str,
    required=True,
    help="path of .h5 file"
)
parser.add_argument(
    "--checkpoint",
    type=str,
    required=True,
    help="path of checkpoint"
)

args = parser.parse_args()


if __name__ == "__main__":
    sys.path.append("../")
    sys.path.append("../src/")
    sys.path.append("../utils/")
    from src.renderer import RenderFromImages, RenderFromEvents
    from src.slomo import SuperSloMo
    from src.reader import Reader

    m = Reader(args.fname, start=args.start, stop=args.stop)
    frames, events = m.read()

    results = []

    with TemporaryDirectory() as dirname:

        print("tmp_dir: ", dirname)

        s = SuperSloMo(
            args.checkpoint,
            10,
            dirname
        )

        s.interpolate(frames["frame"])
        frame_ts = s.get_ts(frames["ts"])
        height, width = frames["frame"].shape[1:]

        r_events = RenderFromEvents(
            frame_ts,
            events,
            "../data/from_event.avi"
        )

        frames_events, num_events = r_events.render(height, width)

        for threshold in np.arange(0.01, 0.2, 0.01):

            r = RenderFromImages(
                dirname,
                frame_ts,
                threshold,
                "../data/from_image_{}.avi".format(threshold))

            frames_images, num_images = r.render(height, width)

            l1_error = np.mean(
                    np.abs(frames_images - frames_events)
                )
            results.append(
                [threshold, np.abs(num_events - num_images), l1_error]
            )
            print("Threshold: {} \t MEAN L1 ERROR: {}".format(threshold,
                                                              l1_error))
    results = np.array(results)
    np.save('../data/results.npy', results)