#!/usr/bin/env python3

"""
    Copyright © 2024 Mia Herkt
    Licensed under the EUPL, Version 1.2 or - as soon as approved
    by the European Commission - subsequent versions of the EUPL
    (the "License");
    You may not use this work except in compliance with the License.
    You may obtain a copy of the license at:

        https://joinup.ec.europa.eu/software/page/eupl

    Unless required by applicable law or agreed to in writing,
    software distributed under the License is distributed on an
    "AS IS" basis, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
    either express or implied.
    See the License for the specific language governing permissions
    and limitations under the License.
"""

import os
import sys
from pathlib import Path

import av
from transformers import pipeline

class NSFWDetector:
    def __init__(self):
        self.classifier = pipeline("image-classification", model="giacomoarienti/nsfw-classifier")

    def detect(self, fpath):
        try:
            with av.open(fpath) as container:
                try: container.seek(int(container.duration / 2))
                except: container.seek(0)

                frame = next(container.decode(video=0))
                img = frame.to_image()
                res = self.classifier(img)

                return max([x["score"] for x in res if x["label"] not in ["neutral", "drawings"]])
        except: pass

        return -1.0

if __name__ == "__main__":
    n = NSFWDetector()

    for inf in sys.argv[1:]:
        score = n.detect(inf)
        print(inf, score)
