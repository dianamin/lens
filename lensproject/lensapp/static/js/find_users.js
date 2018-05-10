let fetchUsers = function() {
	let prefix = document.querySelector('#user-prefix-input').value;
	console.log(prefix);
    let xhttp = new XMLHttpRequest();

    let users = [];

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log(this.response);

            users = JSON.parse(this.response).users;

            showUsers(users);
        }
    };
	
    xhttp.open('GET',
    		   '/ajax/find_user/' + prefix,
    			true);
    xhttp.send();
}

function getLength(users){
	
	return users.length;
}

function getUsername(user){
	return user.username;
}

function getFirstName(user){
	return user.first_name;
}

function getLastName(user){
	return user.last_name;
}

let showUsers =  function(users) {

    let userContainer = document.querySelector('#user-suggestions');

    userContainer.innerHTML = '';
	
	length_user = getLength(users);

    for(let i = 0; i < length_user; i++) {
        userContainer.insertAdjacentHTML('beforeend', '<li class="list-group-item"' + 
            'onclick=openUserPage(' + '"' + getUsername(users[i])+ '"' + ')>' + 
            getFirstName(users[i]) + ' ' + getLastName(users[i]) + 
            '</li>');
    }
	
}

let openUserPage = function(username) {
    window.open('http://127.0.0.1:8000/user/stalk/' + username ,"_self")
}