describe("test", function() {

  it('Should be zero', function() {
    expect(getLength([])).toBe(0);
  });
  
   it('Should be two', function() {
    expect(getLength(["a","b"])).toBe(2);
  });
  
   it('Should be four', function() {
    expect(getLength(["a","b","c","d"])).toBe(4);
  });
  
});