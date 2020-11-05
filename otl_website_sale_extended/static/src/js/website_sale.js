
"use strict";
var myDropzoneOptions = {
    maxFilesize: 4,
    maxFiles: 1,
    addRemoveLinks: true,
    acceptedFiles: 'image/*, .pdf, , .PDF'
}

var myDropzoneContactUsOptions = {
    addRemoveLinks: true,
    url: "/contactus-file-upload",
    maxFiles: 5,
    acceptedFiles: 'image/*, .pdf, , .PDF'
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
                        if (x[2]){
                            fileuploadDropzone.emit("thumbnail", mockFile, x[2]);
                        }
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
            // $("#wrong_files").addClass('d-none');
            $.ajax("/remove/file/" + file.serverID, {
                type: 'POST',
                dataType: 'json',
                success: function(data) {
                    if (data['result']) {
                        file_cntr = parseInt($('#file_count').val());
                        file_cntr--;
                        $('#file_count').val(file_cntr);
                        if (file_cntr == 0) {
                            $('.dz-message').removeClass('d-none');
                        }
                        else{
                            $('.dz-message').addClass('d-none');
                        }
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


    if ($("#dropzone-contactus").length) {
        var file_cntr = 0;
        var fileuploadContactusDropzone = new Dropzone("div#dropzone-contactus", myDropzoneContactUsOptions);


        fileuploadContactusDropzone.on("removedfile", function(file) {
            $.ajax("/remove/contactusfile/" + file.serverID, {
                type: 'POST',
                dataType: 'json',
                success: function(data) {
                    if (data['result']){
                        file_cntr--;
                    }
                },
                error: function(error) {
                    console.log(error)
                }
            });

        });

        fileuploadContactusDropzone.on("error", function(file) {
            setTimeout(function() {
                fileuploadContactusDropzone.removeFile(file);
            }, 0);

            $("#contactus_wrong_files").removeClass('d-none');
            $("#contactus_file_count_validation").addClass('d-none');

        });

        fileuploadContactusDropzone.on("maxfilesexceeded", function(file) {
            $("#contactus_file_count_validation").removeClass('d-none');

        });


        fileuploadContactusDropzone.on("success", function(file, response) {
            file.serverID = response
            $("#contactus_wrong_files").addClass('d-none');
            $("#contactus_file_count_validation").addClass('d-none');
            var dict = {
                'token': $('#contactus_token').val(),
                'attachment_id':file.serverID
            }
            file_cntr++;

            if (file_cntr > 5 ){
                fileuploadContactusDropzone.removeFile(file);
                $("#contactus_file_count_validation").removeClass('d-none');
            }

            new_dict = JSON.stringify(dict);
            $.ajax("/update/contactustoken/" + new_dict, {
                type: 'POST',
                dataType: 'json',
                success: function(data) {
                },
                error: function(error) {
                    console.log(error)
                }
            });
        });

    }

});