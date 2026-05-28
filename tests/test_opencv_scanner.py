from pytest import MonkeyPatch

from wifi_with_camera.scanner import opencv_scanner


def test_list_available_cameras(monkeypatch: MonkeyPatch) -> None:
    released: list[int] = []

    class FakeCapture:
        def __init__(self, index: int) -> None:
            self.index = index

        def isOpened(self) -> bool:
            return self.index in {0, 2}

        def release(self) -> None:
            released.append(self.index)

    def fake_video_capture(index: int) -> FakeCapture:
        return FakeCapture(index)

    monkeypatch.setattr(opencv_scanner, "silence_opencv_logs", lambda: None)
    monkeypatch.setattr(
        "wifi_with_camera.scanner.opencv_scanner.cv2.VideoCapture",
        fake_video_capture,
    )

    result = opencv_scanner.list_available_cameras(max_index=4)

    assert result == [0, 2]
    assert released == [0, 1, 2, 3]
