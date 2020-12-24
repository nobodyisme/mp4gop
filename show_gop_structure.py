#!/usr/bin/env python3
#
# Shows GOP structure of video file. Useful for checking suitability for HLS and DASH packaging.
# Example:
#
# $ iframe-probe.py myvideo.mp4
# GOP: IPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP 60 CLOSED
# GOP: IPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP 60 CLOSED
# GOP: IPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP 60 CLOSED
# GOP: IPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP 60 CLOSED
# GOP: IPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP 60 CLOSED
# GOP: IPPPPPPPPPPPPPPPPP 18 CLOSED
#
# Key:
#     I: IDR Frame
#     i: i frame
#     P: p frame
#     B: b frame

import json
import subprocess
import argparse
import os

import jsonslicer


class BFrame:
    def __repr__(self):
        return "B"
    
    def __str__(self):
        return repr(self)


class PFrame:
    def __repr__(self):
        return "P"

    def __str__(self):
        return repr(self)


class IFrame:
    def __init__(self):
        self.key_frame = False

    def __repr__(self):
        if self.key_frame:
            return "I"
        else:
            return "i"
        
    def __str__(self):
        return repr(self)


class GOP:
    def __init__(self):
        self.closed = False
        self.frames = []
        
    def add_frame(self, frame):
        self.frames.append(frame)
        
        if isinstance(frame, IFrame) and frame.key_frame:
            self.closed = True
            
    def __repr__(self):
        frames_repr = ''
        
        for frame in self.frames:
            frames_repr += str(frame)
        
        gtype = 'CLOSED' if self.closed else 'OPEN'
        
        return 'GOP: {frames} {count} {gtype}'.format(frames=frames_repr, 
                                                      count=len(self.frames), 
                                                      gtype=gtype)


def main():
    parser = argparse.ArgumentParser(description='Dump GOP structure of video file')
    parser.add_argument('filename', help='video file to parse')
    parser.add_argument('-e', '--ffprobe-exec', dest='ffprobe_exec',
                        help='ffprobe executable. (default: %(default)s)',
                        default='ffprobe')
    parser.add_argument('-g', '--gop-count-limit', dest='gop_count_limit',
                        help='Stop scanning gops after this limit',
                        default=None, type=int)

    args = parser.parse_args()

    command = '{ffexec} -show_frames -print_format json {filename}'.format(
        ffexec=args.ffprobe_exec,
        filename=args.filename,
    ).split(' ')

    devnull = open(os.devnull, 'w')
    p = subprocess.Popen(command, stderr=devnull, stdout=subprocess.PIPE)

    gops = []
    gop = GOP()
    gops.append(gop)

    gops_count = 0

    for jframe in jsonslicer.JsonSlicer(p.stdout, ('frames', None)):
        if jframe["media_type"] == "video":

            frame = None

            if jframe["pict_type"] == 'I':
                if len(gop.frames):
                    print(gop)
                gops_count += 1
                if args.gop_count_limit and gops_count > args.gop_count_limit:
                    break
                if len(gop.frames):
                    # GOP open and new iframe. Time to close GOP
                    gop = GOP()
                    gops.append(gop)
                frame = IFrame()
                if jframe["key_frame"] == 1:
                    frame.key_frame = True
            elif jframe["pict_type"] == 'P':
                frame = PFrame()
            elif jframe["pict_type"] == 'B':
                frame = BFrame()

            frame.json = jframe
            gop.add_frame(frame)


if __name__ == '__main__':
    main()
