document.getElementById('sidebarToggle').addEventListener('click', function() {
    var sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('sidebar-closed');
});
function refreshPdfSelection() {
    $.get('/get-classes', function(data) {
        var classDropdown = $('#doc-select');
        classDropdown.empty();
        classDropdown.append('<option value="" selected>Select PDF</option>');
        data.class_list.forEach(function(item, index) {
            classDropdown.append('<option value="' + (index + 1) + '">' + item + '</option>');
        });
    });
}
// Initialize Dropzone
Dropzone.options.myDropzone = {
    url: '/upload',
    paramName: "file", // The name that will be used to transfer the file
    maxFilesize: 5, // MB
    addRemoveLinks: true,
    acceptedFiles: ".pdf", // Add your required file formats here
    init: function() {
        this.on("success", function(file, response) {
            console.log(response);  // Handle the response from server after upload
            refreshPdfSelection();  // Refresh the PDF selection dropdown
            this.removeAllFiles();
        });
    }
};
Dropzone.autoDiscover = false;
var myDrop = new Dropzone("#myDropzone", {
    url: '/upload',
    paramName: "file",
    maxFilesize: 5,
    addRemoveLinks: true,
    acceptedFiles: ".pdf",
    dictDefaultMessage: "click, tap or drop PDFs to semantic search", 
    init: function() {
        this.on("success", function(file, response) {
            console.log(response);
            refreshPdfSelection();  // Refresh the PDF selection dropdown
            this.removeAllFiles();
        });
    }
});

$(document).ready(function() {
    // Populate the class choices dropdown
    $.get('/get-classes', function(data) {
        var classDropdown = $('#doc-select');
        classDropdown.empty();
        classDropdown.append('<option value="" selected>Select PDF</option>');
        data.class_list.forEach(function(item, index) {
            classDropdown.append('<option value="' + (index + 1) + '">' + item + '</option>');
        });
    });

    $('#chat-form').on('submit', function(e) {
        e.preventDefault();
        var message = $('#message').val();
        var classChoice = $('#doc-select').val();  // get selected class choice
        var pageLimit = $('#page-limit-select').val();  // get selected page limit
        $.post('/search', {class_choice: classChoice, query: message, page_limit: pageLimit}, function(data) {
            var d = new Date();
            var timeStamp = d.getHours() + ":" + d.getMinutes() + ":" + d.getSeconds();
            $('#chatbox').append('<div class="message user-message p-2 mb-2 rounded"><strong>You:</strong> ' + message + '<span class="timestamp float-right">' + timeStamp + '</span></div>');
            for(var i = 0; i < data.length; i++) {
                var responseText = data[i].response_text;
                var title = data[i].title;
                var confidence = (data[i].confidence_percentage).toFixed(2) + '%';
                var content = data[i].content.replace(/\n/g, '<br>');
                var responseHtml = '<div class="message bot-message p-2 mb-2 rounded"><strong>Chatbot:</strong> ' + responseText;
                responseHtml += '<br><strong>Title:</strong> ' + title;
                responseHtml += '<br><strong>Confidence:</strong> ' + confidence;
                responseHtml += '<details><summary>View Source Document</summary><strong>Source Document Content:</strong><br>' + content + '</details>';
                responseHtml += '<span class="timestamp float-right">' + timeStamp + '</span></div>';
                $('#chatbox').append(responseHtml);
            }
            $('#message').val('');
            $('#chatbox').scrollTop($('#chatbox')[0].scrollHeight);
            // Highlight any code blocks
            $('pre code').each(function(i, block) {
                hljs.highlightBlock(block);
            });
        });
    });
});