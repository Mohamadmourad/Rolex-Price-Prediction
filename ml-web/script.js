let session;
let mappings = {};

async function loadModel() {
  try {
    session = await ort.InferenceSession.create("knn_model.onnx");
    console.log("Model loaded");
  } catch (err) {
    console.error("Error loading model:", err);
  }
}

async function loadMappings() {
  try {
    const response = await fetch("mappings.json");
    mappings = await response.json();
    console.log("Mappings loaded:", mappings);
  } catch (err) {
    console.error("Error loading mappings:", err);
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  await loadMappings();
  await loadModel();
});

document
  .getElementById("predict-form")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    const inputs = {
      model: mappings["Model"][document.getElementById("model").value] ?? 0,
      caseMaterial:
        mappings["Case Material"][
          document.getElementById("case-material").value
        ] ?? 0,
      braceletMaterial:
        mappings["Bracelet Material"][
          document.getElementById("bracelet-material").value
        ] ?? 0,
      year: parseInt(document.getElementById("year").value) || 0,
      gender: mappings["Gender"][document.getElementById("gender").value] ?? 0,
      jewels: parseInt(document.getElementById("jewels").value) || 0,
      claspMaterial:
        mappings["Clasp Material"][
          document.getElementById("clasp-material").value
        ] ?? 0,
    };

    console.log("Inputs:", inputs);

    const featureVector = Float32Array.from([
      inputs.model,
      inputs.caseMaterial,
      inputs.braceletMaterial,
      inputs.year,
      inputs.gender,
      inputs.jewels,
      inputs.claspMaterial,
    ]);
    console.log("Feature Vector:", featureVector);

    const inputTensor = new ort.Tensor("float32", featureVector, [1, 7]);

    if (!session) {
      console.error("Model not loaded yet.");
      return;
    }

    try {
      const feeds = { float_input: inputTensor };
      console.log("Feeds:", feeds);
      const results = await session.run(feeds);
      console.log("Model Results:", results);
      const [outputName] = session.outputNames;
      const prediction = results[outputName].data[0];
      console.log("Prediction:", prediction);

      document.getElementById("price").innerText = `$${prediction.toFixed(2)}`;
    } catch (err) {
      console.error("Error during model inference:", err);
    }
  });
