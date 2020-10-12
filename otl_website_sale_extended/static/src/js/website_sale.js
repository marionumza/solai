
"use strict";
var myDropzoneOptions = {
    maxFilesize: 4,
    maxFiles: 1,
    addRemoveLinks: true,
    acceptedFiles: 'image/*'
}


$(document).ready(function() {

	if ($("#dropzone-products-checkout").length) {
		var fileuploadDropzone = new Dropzone("#dropzone-products-checkout", myDropzoneOptions);
        var file_cntr = 0;
        var edit = $('#edit').val()
        if (edit){
            // $("#dropzone-products-checkout").dropzone({
              // init: function() { 
            $.ajax({
              url: '/GetUploadedImages',
              type: 'post',
              data: {},
              dataType: 'json',
              success: function(response){
                if (response.images.length) {
                    $('.dz-message').addClass('d-none');
                    _.each(response.images, function(x) {
                        var mockFile = {name: x[0],serverID:x[1] };
                        fileuploadDropzone.emit("addedfile", mockFile);
                        fileuploadDropzone.emit("thumbnail", mockFile, x[2]);
                        fileuploadDropzone.emit("complete", mockFile);
                    });
                    $('#edit').val("");
                }

              },
              error: function(error) {
                }
            });
              // }
            // });
        }
         
        fileuploadDropzone.on("addedfile", function(file) {   

        });

        fileuploadDropzone.on("removedfile", function(file) {
            $("#file_count_validation").addClass('d-none');
            $("#wrong_files").addClass('d-none');
            $.ajax("/remove/file/" + file.serverID, {
                type: 'POST',
                dataType: 'json',
                success: function(data) {
                    file_cntr = parseInt($('#file_count').val());
                    file_cntr--;
                    $('#file_count').val(file_cntr);
                    if (file_cntr == 0) {
                        $('.dz-message').removeClass('d-none');
                    }
                    else{
                        $('.dz-message').addClass('d-none');    
                    }
                },
                error: function(error) {
                    console.log(error)
                }
            });

        });

        fileuploadDropzone.on("error", function(file) {
            setTimeout(function() {
                fileuploadDropzone.removeFile(file);
            }, 0);
            $('#wrong_files').removeClass('d-none');

        });

        fileuploadDropzone.on("maxfilesexceeded", function(file) {
            $("#files_count_validation").removeClass('d-none');

        });

        fileuploadDropzone.on("success", function(file, response) {
            file.serverID = response
            if ($('#file_count').val()){
                file_cntr = parseInt($('#file_count').val());    
            }
            else{
                file_cntr = 0
            }
            
            file_cntr++;
            $('#file_count').val(file_cntr);
            if (file_cntr >= 1){
                $('.dz-message').addClass('d-none');
            }
            else{
                $('.dz-message').removeClass('d-none');  
            }
            $(".dz-success-mark svg").css("background", "green");
            $('#wrong_files').addClass('d-none');
            $('#no_files').addClass('d-none');
            if (file_cntr > 5 ){
                fileuploadDropzone.removeFile(file);
                $("#file_count_validation").removeClass('d-none');
            }
        });
     
    }

});