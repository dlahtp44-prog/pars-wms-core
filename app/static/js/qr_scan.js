
// Lightweight QR scan using ZXing CDN
let codeReader;

async function startScan(inputId) {
  if (!window.ZXing) {
    alert("ZXing 라이브러리를 불러오지 못했습니다.");
    return;
  }
  codeReader = new ZXing.BrowserQRCodeReader();
  const videoInputDevices = await ZXing.BrowserQRCodeReader.listVideoInputDevices();
  const firstDeviceId = videoInputDevices[0]?.deviceId;
  if (!firstDeviceId) {
    alert("카메라를 찾을 수 없습니다.");
    return;
  }
  codeReader.decodeFromVideoDevice(firstDeviceId, 'video', (result, err) => {
    if (result) {
      document.getElementById(inputId).value = result.text;
      stopScan();
    }
  });
}

function stopScan() {
  if (codeReader) {
    codeReader.reset();
  }
}
