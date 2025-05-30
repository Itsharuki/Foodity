//##############################################################################
//#####################  D A S H B O A R D  C O U N T E R  #####################
//##############################################################################



function countRow(){
    var rowCount_seller = document.getElementById('seller_table_id');
    var total_rowCount = seller_table_id.tBodies[0].rows.length;
    document.getElementById('sellerCount').innerHTML = total_rowCount;

    var rowCount_buyer = document.getElementById('buyer_table_id');
    var total_BuyersRow = buyer_table_id.tBodies[0].rows.length;
    document.getElementById('buyerCount').innerHTML = total_BuyersRow;

    const date = new Date();
    yesterday = date.setDate(date.getDate() - 1);

    yesterday_value = total_rowCount 

}
