var p_SKU = function () {

    return {
        //main function to initiate the module
        init: function () {



            $('#downloadSKUTemplate').click(function () {
                window.location.href="download"
            });

        }

    };

}();

jQuery(document).ready(function() {    
   p_SKU.init();
});
