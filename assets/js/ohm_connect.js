/* Put common javascript here */

function tabShow(selector) {
    var $this = $(selector);
    var $ul = $this.closest('ul:not(.dropdown-menu)');
    $ul.find('li').removeClass('active');
    $this.addClass('active')
}

Number.prototype.formatMoney = function (places, symbol, thousand, decimal) {
    places = !isNaN(places = Math.abs(places)) ? places : 2;
    symbol = symbol !== undefined ? symbol : "$";
    thousand = thousand || ",";
    decimal = decimal || ".";
    var number = this,
        negative = number < 0 ? "-" : "",
        i = parseInt(number = Math.abs(+number || 0).toFixed(places), 10) + "",
        j = (j = i.length) > 3 ? j % 3 : 0;
    return symbol + negative + (j ? i.substr(0, j) + thousand : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + thousand) + (places ? decimal + Math.abs(number - i).toFixed(places).slice(2) : "");
};

function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function checkToast(msg, timeout) {
    if (typeof timeout === 'undefined'){
        timeout = 5000
    }

    if (typeof(msg) == 'string' && msg.length > 0) {
        $.snackbar({content: msg, timeout: timeout})
    }
}

function clickToDismiss(msg){
  // a timeout of 0 means it requires a click to dismiss...
  checkToast(msg, 0)
}

$(document).ready(function () {
    // MD Jan-2015 The "toast" variable is declared and set in base_map.html
    checkToast(toast)

    $('[data-toggle="tooltip"]').tooltip({
      html: true
    })
});
