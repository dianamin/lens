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

let showUsers =  function(users) {

    let userContainer = document.querySelector('#user-suggestions');

    userContainer.innerHTML = '';

    for(let i = 0; i < users.length; i++) {
        userContainer.insertAdjacentHTML('beforeend', '<li class="list-group-item"' + 
            'onclick=openUserPage(' + '"' + users[i].username + '"' + ')>' + 
            users[i].first_name + ' ' + users[i].last_name + 
            '</li>');
    }
    
}

let openUserPage = function(username) {
    window.open('http://127.0.0.1:8000/user/stalk/' + username ,"_self")
}