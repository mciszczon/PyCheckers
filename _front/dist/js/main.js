$(document).ready( function(){
    // Copy to clipboard
    var clipboard = new Clipboard('#copy-url-button');
    clipboard.on('success', function(e) {
        $(e.trigger).attr('data-tooltip', 'Copied to clipboard!').addClass('active');
        setTimeout(function() {
            $(e.trigger).attr('data-tooltip', '').removeClass('active')
          }, 3000)
    });
});