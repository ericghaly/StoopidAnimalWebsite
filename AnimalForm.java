public class AnimalForm {
	
	@Constraints.Required
	protected String name;
	protected String description;
	//images
	
	public String validate() {
		if(authenticate(name, description) == null){
			return "Invalid Name Or Description";
		}
		return null;
	} 
	
	public void setName(String name){ this.name = name; }
	
	public String getName(){ return this.name; }
	
	public void setDescription(String description) { this.description = description; }
	
	public String getDescription(){ return this.description; }
	
}


public static void main(){
	Form<AnimalForm> createForm = formFactory.form(AnimalForm.class);
	AnimalForm form = new AnimalForm();
	form.setName("dog");
	form.setDescription("mans best friend");
	
	Map<String,String> data = new HashMap();
	
	data.put("name", form.getName());
	data.put("description", form.getDescription();
		