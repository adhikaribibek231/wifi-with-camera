from dataclasses import dataclass

import numpy as np
import zxingcpp  # type: ignore[import-not-found]
from numpy.typing import NDArray

Frame = NDArray[np.uint8]


@dataclass(frozen=True)
class QRDecodeResult:
    text: str


class ZXingQRDecoder:
    def decode(self, frame: Frame) -> QRDecodeResult | None:
        results = zxingcpp.read_barcodes(frame)

        if not results:
            return None

        return QRDecodeResult(text=results[0].text)
