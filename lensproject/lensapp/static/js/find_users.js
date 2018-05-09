let fetchUsers = function() {
	let prefix = document.querySelector('#user-prefix-input').value;
	console.log(prefix);
    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log(this.response);
        }
    };
    xhttp.open('GET',
    		   '/ajax/find_user/' + prefix,
    			true);
    xhttp.send();
}