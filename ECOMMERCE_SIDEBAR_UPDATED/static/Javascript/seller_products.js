function Add_New_Product(){
    var add_form = document.getElementById('add_form');
    add_form.classList.toggle('active');
}

function Close_AddProduct(){
    var close_button = document.getElementById('add_form');
    close_button.classList.toggle('active');
}



function change_pic1(){
    productImage = document.getElementById("image_view1");
    productFile = document.getElementById("productImage1");
    productImage.src = URL.createObjectURL(productFile.files[0]);
    if(productFile.files[0].size > 1e+6){
        alert("File is too big!")
        productFile.value = ""
    }
}

function change_pic2(){
    productImage = document.getElementById("image_view2");
    productFile = document.getElementById("productImage2");
    productImage.src = URL.createObjectURL(productFile.files[0]);
    if(productFile.files[0].size > 1e+6){
        alert("File is too big!")
        productFile.value = ""
    }
}

function change_pic3(){
    productImage = document.getElementById("image_view3");
    productFile = document.getElementById("productImage3");
    productImage.src = URL.createObjectURL(productFile.files[0]);
    if(productFile.files[0].size > 1e+6){
        alert("File is too big!")
        productFile.value = ""
    }
}

function change_pic4(){
    productImage = document.getElementById("image_view4");
    productFile = document.getElementById("productImage4");
    productImage.src = URL.createObjectURL(productFile.files[0]);
    if(productFile.files[0].size > 1e+6){
        alert("File is too big!")
        productFile.value = ""
    }
}