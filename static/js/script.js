document.addEventListener('DOMContentLoaded', function () {
    const symptomList = document.getElementById('symptom-list');
    const symptomsInput = document.getElementById('symptoms-input');
    const predictButton = document.getElementById('predictButton');
    const clearButton = document.getElementById('clearButton');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const symptomCountDisplay = document.getElementById('symptom-count');

    let selectedSymptoms = [];

    // FIX 10.1: toSnakeCase helper function ADDED. Ha function addSymptom sathi necessary ahe.
    function toSnakeCase(str) {
        if (!str) return '';
        // Lowercase, replace spaces with underscore, trim
        return str.toLowerCase().trim().replace(/\s+/g, '_'); 
    }

    function autocomplete(inp, arr) {
        let currentFocus;

        inp.addEventListener("input", function (e) {
            let a, b, i, val = this.value;
            closeAllLists();
            if (!val) {
                if (selectedSymptoms) {
                    updateSymptomCount();
                }
                return false;
            }
            currentFocus = -1;
            a = document.createElement("DIV");
            a.setAttribute("id", this.id + "autocomplete-list");
            a.setAttribute("class", "autocomplete-items");
            this.parentNode.appendChild(a);
            for (i = 0; i < arr.length; i++) {
                // Check for case-insensitive start-of-string match
                if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
                    b = document.createElement("DIV");
                    b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
                    b.innerHTML += arr[i].substr(val.length);
                    // Hidden input madhye original title case symptom value store kara
                    b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>"; 
                    b.addEventListener("click", function (e) {
                        // Title Case symptom value input madhun gheun addSymptom la dya
                        const selectedValue = this.getElementsByTagName("input")[0].value;
                        inp.value = selectedValue; 
                        addSymptom(selectedValue);
                        closeAllLists();
                    });
                    a.appendChild(b);
                }
            }
        });
        inp.addEventListener("keydown", function (e) {
            let x = document.getElementById(this.id + "autocomplete-list");
            if (x) x = x.getElementsByTagName("div");
            if (e.keyCode == 40) {
                currentFocus++;
                addActive(x);
            } else if (e.keyCode == 38) { //up
                currentFocus--;
                addActive(x);
            } else if (e.keyCode == 13) {
                e.preventDefault();
                if (currentFocus > -1) {
                    if (x) x[currentFocus].click();
                }
            }
        });
        function addActive(x) {
            if (!x) return false;
            removeActive(x);
            if (currentFocus >= x.length) currentFocus = 0;
            if (currentFocus < 0) currentFocus = (x.length - 1);
            x[currentFocus].classList.add("autocomplete-active");
        }
        function removeActive(x) {
            for (let i = 0; i < x.length; i++) {
                x[i].classList.remove("autocomplete-active");
            }
        }
        function closeAllLists(elmnt) {
            let x = document.getElementsByClassName("autocomplete-items");
            for (let i = 0; i < x.length; i++) {
                if (elmnt != x[i] && elmnt != inp) {
                    x[i].parentNode.removeChild(x[i]);
                }
            }
        }
        document.addEventListener("click", function (e) {
            closeAllLists(e.target);
        });
    }

    function updateSymptomCount() {
        const symptomCountDisplay = document.getElementById('symptom-count');
        
        // MIN_SYMPTOMS value DOM madhun read kara.
        const hintElement = document.querySelector('.symptom-hint');
        let minSymptoms = '7'; // Default value

        if (hintElement) {
            const match = hintElement.textContent.match(/\d+/);
            if (match) {
                minSymptoms = match[0];
            }
        }
        symptomCountDisplay.textContent = `Total Symptoms: ${selectedSymptoms.length}. Minimum required: ${minSymptoms}.`; 
    }

    // FIX: symptom Title Case madhun yeto, pan snake_case madhye store hoto.
    function addSymptom(symptom) {
        const snakeCaseSymptom = toSnakeCase(symptom); 
        if (!selectedSymptoms.includes(snakeCaseSymptom)) {
            selectedSymptoms.push(snakeCaseSymptom); 
            updateSymptomList();
            symptomsInput.value = '';
        }
    }

    function removeSymptom(snakeCaseSymptom) { // Input is snake_case
        selectedSymptoms = selectedSymptoms.filter(s => s !== snakeCaseSymptom);
        updateSymptomList();
    }

    function updateSymptomList() {
        symptomList.innerHTML = '';
        selectedSymptoms.forEach(snakeCaseSymptom => { // Array madhye snake_case symptoms ahet
            const li = document.createElement('li');
            
            // Display sathi, snake_case la Title Case with Spaces madhye parat convert kara
            const displaySymptom = snakeCaseSymptom.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
            li.textContent = displaySymptom;
            
            // FIX: Unrecognized symptom check block removed (Step 10)
            
            const removeButton = document.createElement('button');
            removeButton.classList.add('remove-symptom');
            removeButton.textContent = 'Remove';
            // removeSymptom la snake_case symptom pass kara
            removeButton.addEventListener('click', () => removeSymptom(snakeCaseSymptom));
            li.appendChild(removeButton);
            symptomList.appendChild(li);
        });
        updateSymptomCount();
    }

    // Autocomplete initialize kara (symptomIndex keys Title Case with Spaces madhye ahet)
    autocomplete(symptomsInput, Object.keys(window.symptomIndex || {}));

    const clearButtonElement = document.getElementById('clearButton');
    if (clearButtonElement) {
        clearButtonElement.addEventListener('click', function () {
            selectedSymptoms = [];
            updateSymptomList();
            updateSymptomCount();
            const resultsSection = document.querySelector('.results-section');
            if (resultsSection) {
                resultsSection.style.display = 'none';
            }
            predictButton.disabled = false;
            clearButton.disabled = false;
            loadingIndicator.style.display = 'none';
        });
    }

    document.querySelector('form').addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent the default form submission

        predictButton.disabled = true;
        clearButton.disabled = true;
        loadingIndicator.style.display = 'block';

        // Create a hidden input to send the selected symptoms
        const hiddenInput = document.createElement('input');
        hiddenInput.setAttribute('type', 'hidden');
        hiddenInput.setAttribute('name', 'symptoms');
        
        // selectedSymptoms madhye snake_case values ahet, je backend la pathva
        hiddenInput.setAttribute('value', selectedSymptoms.join(','));
        this.appendChild(hiddenInput);

        // Submit the form programmatically
        this.submit();
    });
});