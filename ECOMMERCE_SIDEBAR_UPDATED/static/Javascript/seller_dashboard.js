function countRow(){
    var rowCount_seller = document.getElementById('orders_table_id');
    var total_rowCount = orders_table_id.tBodies[0].rows.length;
    document.getElementById('ordersCount').innerHTML = total_rowCount;

    var rowCount_buyer = document.getElementById('delivered_table_id');
    var total_BuyersRow = delivered_table_id.tBodies[0].rows.length;
    document.getElementById('deliveredCount').innerHTML = total_BuyersRow;

    var rowCount_buyer = document.getElementById('cancelled_table_id');
    var total_BuyersRow = cancelled_table_id.tBodies[0].rows.length;
    document.getElementById('cancelledCount').innerHTML = total_BuyersRow;
}

function showDropdown(){
    document.getElementById("dropdown_profile").classList.toggle("show");
}

window.onclick = function(event){
    if (!event.target.matches('.profile_button')){
        var profile_dropdown = document.getElementsByClassName("profile_dropdown_content");
        var i;

        for (i = 0; i< profile_dropdown.length; i++){
            var open_profileDropdown = profile_dropdown[i];
            if (open_profileDropdown.classList.contains('show')){
                open_profileDropdown.classList.remove('show');
            }
        }
    }
}