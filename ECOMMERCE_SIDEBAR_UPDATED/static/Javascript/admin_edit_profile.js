
function change_pic(){
    profilePic = document.getElementById("profile_pic");
    inputFile = document.getElementById("input_image");
    profilePic.src = URL.createObjectURL(inputFile.files[0]);
    if(inputFile.files[0].size > 1e+6){
        alert("File is too big!")
        inputFile.value = ""
    }
}