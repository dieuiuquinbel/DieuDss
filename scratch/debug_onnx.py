import sys

with open("scratch/onnx_error.log", "w", encoding="utf-8") as out:
    try:
        import onnxruntime as ort
        out.write(f"onnxruntime version: {ort.__version__}\n")
        session = ort.InferenceSession("models/vnfood_mobilenet_v3.onnx", providers=['CPUExecutionProvider'])
        out.write(f"Success! Inputs: {[i.name for i in session.get_inputs()]}\n")
    except Exception as e:
        out.write(f"Exception: {type(e).__name__}: {str(e)}\n")
        import traceback
        traceback.print_exc(file=out)

print("Done checking ONNX load")
