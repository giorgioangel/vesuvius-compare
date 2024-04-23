document.addEventListener("DOMContentLoaded", function() {
    const generateButton = document.getElementById('generateButton');
    const sampleButton = document.getElementById('sampleButton');

    generateButton.addEventListener('click', function(event) {
        const radius = document.getElementById('radius');
        const centerZ = document.getElementById('centerZ');
        const centerY = document.getElementById('centerY');
        const centerX = document.getElementById('centerX');

        // Validate each field
        let isRValid = validateRadius(radius);
        let isZValid = validateInput(centerZ, 14000);
        let isYValid = validateInput(centerY, 7500);
        let isXValid = validateInput(centerX, 8000);

        // Check if all validations passed
        if (!isRValid || !isZValid || !isYValid || !isXValid) {
            // If any validation fails, prevent fetching data
            event.preventDefault(); // This stops the form from submitting or any other default action
            return false; // Stop further execution
        }
        fetchAndDisplayData();
    });

    sampleButton.addEventListener('click', function(event) {
        const radius = document.getElementById('radius');

        // Validate radius
        let isRValid = validateRadius(radius);

        // Check if validation passed
        if (!isRValid) {
            // If validation fails, prevent fetching data
            event.preventDefault(); // This stops the form from submitting or any other default action
            return false; // Stop further execution
        }
        fetchAndDisplayData(true);
    });

    function validateInput(input, max) {
        const min = 500;
        const value = parseInt(input.value, 10);

        if (isNaN(value)) { // Ensure the input is a number
            alert("Please enter a valid number");
            return false;
        }

        if (value > max) {
            alert(`Value should not be greater than ${max}`);
            return false; // Indicate that validation failed
        } else if (value < min) {
            alert(`Value should not be less than ${min}`);
            return false; // Indicate that validation failed
        }
        return true; // Validation passed
    }

    function validateRadius(input) {
        const min = 30;
        const max = 500; // Corrected to close the declaration properly
        const value = parseInt(input.value, 10);

        if (isNaN(value)) { // Ensure the input is a number
            alert("Please enter a valid number");
            return false;
        }

        if (value > max) {
            alert(`Value should not be greater than ${max}`);
            return false; // Indicate that validation failed
        } else if (value < min) {
            alert(`Value should not be less than ${min}`);
            return false; // Indicate that validation failed
        }
        return true; // Validation passed
    }
});

        function fetchAndDisplayData(useRandom = false) {
            const methodA = document.getElementById('methodA').value;
            const methodB = document.getElementById('methodB').value;
            // Collect center coordinates only if useRandom is false
            const radius = document.getElementById('radius').value;
            const centerZ = useRandom ? '' : document.getElementById('centerZ').value;
            const centerY = useRandom ? '' : document.getElementById('centerY').value;
            const centerX = useRandom ? '' : document.getElementById('centerX').value;

            document.getElementById('methodA-title').textContent = 'Method A: ' + methodA;
            document.getElementById('methodB-title').textContent = 'Method B: ' + methodB;
            
            document.getElementById('loading').style.display = 'block';
            document.getElementById('dataVisualization').style.display = 'none'; // To reveal the visualization
            document.getElementById('votePanel').style.display = 'none';
            // Update the title for Volume Slices
            let titleText = `Volume of radius: ${radius}`;
            if (!useRandom && centerZ !== "" && centerY !== "" && centerX !== "") {
                titleText += ` at (Z: ${centerZ}, Y: ${centerY}, X: ${centerX})`;
            } else {
                titleText += ' sampled at random coordinates';
            }
            document.getElementById('commonSlicesVisualizer').getElementsByClassName('sub-title')[0].textContent = titleText;

            // Construct the API endpoint with optional center parameters
            let endpoint = `/generate?methodA=${methodA}&methodB=${methodB}&radius=${radius}`;
            if (!useRandom && centerZ !== "" && centerY !== "" && centerX !== "") {
                endpoint += `&centerZ=${centerZ}&centerY=${centerY}&centerX=${centerX}&radius=${radius}`;
            }

            fetch(endpoint)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('dataVisualization').style.display = 'flex'; // To reveal the visualization
                    document.getElementById('votePanel').style.display = 'flex';
                    document.getElementById('currentHash').value = data.hash;
                    document.getElementById('methodA-title').textContent = document.getElementById('methodA-title').textContent + ' ' + `${data.time1.toFixed(5)} s`
                    document.getElementById('methodB-title').textContent = document.getElementById('methodB-title').textContent + ' ' + `${data.time2.toFixed(5)} s`
                    // Display metrics
                    document.getElementById('metricsDisplay').innerHTML = `
                        Hausdorff Distance: ${data.metrics.hausdorff_distance.toFixed(3)}<br>
                        Chamfer Distance: ${data.metrics.chamfer_distance.toFixed(3)}, Chamfer A to B: ${data.metrics.chamfer_12.toFixed(3)}, Chamfer B to A: ${data.metrics.chamfer_21.toFixed(3)},<br>
                        Normals Distance: ${data.metrics.normals_distance.toFixed(3)}, Normals A to B: ${data.metrics.normals_12.toFixed(3)}, Normals B to A: ${data.metrics.normals_21.toFixed(3)}
                        `;
                    document.getElementById('vviewer0').src = `volumes.html?volume=${data.hash}_volume`;
                    document.getElementById('vviewer1').src = `volumes.html?volume=${data.hash}_1`;
                    document.getElementById('vviewer2').src = `volumes.html?volume=${data.hash}_2`;
                    loadAndPlot(`/clouds/${data.hash}_1.ply`, data.color1, 1, leftVisualizer);
                    loadAndPlot(`/clouds/${data.hash}_2.ply`, data.color2, 2, rightVisualizer);
                })
                .catch(error => {
                    console.error('Error loading data:', error);
                    document.getElementById('loading').innerHTML = 'Error during data generation.';
                });
        }


        function displayParameters(params, containerId) {
            const container = document.getElementById(containerId);
            container.innerHTML = ''; // Clear previous content
            Object.keys(params).forEach(key => {
                const value = params[key];
                const node = document.createElement('p');
                node.textContent = `${key}: ${value}`;
                container.appendChild(node);
            });
        }

        function loadAndPlot(cloudId, colorId, number, containerId) {
            fetch(cloudId)
                .then(response => response.json())
                .then(data => {
                    const trace = {
                        x: data.map(point => point[0]),
                        y: data.map(point => point[1]),
                        z: data.map(point => point[2]),
                        mode: 'markers',
                        type: 'scatter3d',
                        marker: {
                            size: document.getElementById(`sizeSlider${number}`).value,
                            opacity: 0.8,
                            color: colorId
                        }
                    };
                    const layout = {
                        autosize: true,
                        margin: { l: 0, r: 0, b: 0, t: 0 },
                        scene: { aspectmode: 'cube' }
                    };
                    Plotly.newPlot(containerId, [trace], layout);
                });
            document.getElementById(`sizeSlider${number}`).addEventListener('input', function() {
                updatePlotSize(containerId, this.value);
            });
        }

        function updatePlotSize(containerId, newSize) {
            const update = {
                'marker.size': [newSize]
            };
            Plotly.restyle(containerId, update);
        }

        function vote(option) {
            const hash = document.getElementById('currentHash').value; // Assuming you store the hash in an input field
            fetch('/vote', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ hash: hash, winner: option })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Vote recorded:', data);
                alert(`Voted for option ${option}`);
                window.location.href = '/'; // Redirect to the home page
            })
            .catch(error => {
                console.error('Error recording vote:', error);
                alert('Failed to record vote. Please try again.');
            });
        }