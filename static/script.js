const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const dropZoneText = document.getElementById('drop-zone-text');
const form = document.getElementById('upload-form');
const progressContainer = document.getElementById('progress-container');
const progressBar = document.getElementById('progress-bar');

// Drag & Drop
dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', e => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', e => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', e => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    fileInput.files = e.dataTransfer.files;
    if(fileInput.files.length > 0){
        dropZoneText.textContent = fileInput.files[0].name;
    }
});

// Show selected file when using file input
fileInput.addEventListener('change', () => {
    if(fileInput.files.length > 0){
        dropZoneText.textContent =  fileInput.files[0].name;
    } else {
        dropZoneText.textContent = "اسحب وافلت ملف الاكسل هنا\nأو اضغط لاختياره";
    }
});

// Gender toggle
const genderFilter = document.getElementById('gender_filter');
const genderSelect = document.getElementById('gender_select');

genderFilter.addEventListener('change', () => {
    if (genderFilter.value === 'yes') {
        genderSelect.classList.remove('hidden');
        genderSelect.classList.add('show');
    } else {
        genderSelect.classList.remove('show');
        genderSelect.classList.add('hidden');
    }
});

// Manual fields toggle
const manualSelect = document.getElementById('manual_select');
const manualFields = document.getElementById('manual-fields');

manualSelect.addEventListener('change', () => {
    if (manualSelect.value === 'yes') {
        manualFields.classList.remove('hidden');
        manualFields.classList.add('show');
    } else {
        manualFields.classList.remove('show');
        manualFields.classList.add('hidden');
    }
});


// Submit with AJAX
form.addEventListener('submit', function(e){
    e.preventDefault();

    if(fileInput.files.length === 0) return;

    const formData = new FormData(form);
    const originalFileName = fileInput.files[0].name;
    const vcfFileName = originalFileName.replace(/\.[^/.]+$/, ".vcf");

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/upload', true);

    xhr.upload.addEventListener('progress', function(e){
        if(e.lengthComputable){
            const percent = Math.round((e.loaded / e.total) * 100);
            progressContainer.style.display = 'block';
            progressBar.style.width = percent + '%';
            progressBar.textContent = percent + '%';
        }
    });

    xhr.onload = function(){
        if(xhr.status === 200){
            const blob = new Blob([xhr.response], {type: "application/octet-stream"});
            const link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = vcfFileName;
            link.click();
            progressBar.textContent = "✅ تم التحويل!";
        } else {
            progressBar.textContent = "❌ حدث خطأ!";
        }
    };

    xhr.responseType = 'blob';
    xhr.send(formData);
});
