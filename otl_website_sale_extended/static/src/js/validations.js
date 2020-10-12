odoo.define('otl_website_sale_extended.validations', function(require) {
"use strict";

    function post(path, params, method = 'post') {
        const form = document.createElement('form');
        form.method = method;
        form.action = path;

        for (const key in params) {
            if (params.hasOwnProperty(key)) {
                const hiddenField = document.createElement('input');
                hiddenField.type = 'hidden';
                hiddenField.name = key;
                hiddenField.value = params[key];

                form.appendChild(hiddenField);
            }
        }

        document.body.appendChild(form);
        form.submit();
    }

    $(".upload_btn_w").click(function(){
        var count = $('#file_count').val();
        if (count == 0 || count == ''){
            $('#no_files').removeClass('d-none');
        }
        else{
            $('#no_files').addClass('d-none');
            $("#shop_products_checkout").submit();    
        }
    });  

});