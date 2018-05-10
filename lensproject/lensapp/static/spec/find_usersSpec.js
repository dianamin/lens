describe("displaying found users", function() {

  it('Should be zero users', function() {
	  
    expect(getLength([])).toBe(0);
	
  });
  
   it('Should be two users', function() {
	   
    expect(getLength(["a","b"])).toBe(2);
	
  });
  
   it('Should be four users', function() {
	   
    expect(getLength(["a","b","c","d"])).toBe(4);
	
  });
  
});

describe("displaying first name, last name and username", function() {

  var person = {username:"JohnDoe", first_name:"John", last_name:"Doe"};
  
  it('Should be John', function() {
	  
    expect(getFirstName(person)).toBe("John");
	
  });
  
   it('Should be JohnDoe', function() {
	   
    expect(getUsername(person)).toBe("JohnDoe");
	
  });
  
   it('Should be Doe', function() {
	   
    expect(getLastName(person)).toBe("Doe");
	
  });
  
  it('Should be object type', function() {
	  
	  expect(person).toEqual(jasmine.any(Object));
  });
  
});

