package pa03_osn;

import java.io.*;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.Map.Entry;

import com.google.common.base.Joiner;

public class Client_Data{

	// class data member
	private String userId;
	private String firstName;
	private String lastName;
	private String ip;
	private Integer port;
	private Vector<String> friends;
	private Map<String, Integer> chats;
	private Map<Date, String> posts;
	private SimpleDateFormat sdf;
	
	// class constructor
	Client_Data(String userId, String firstName, String lastName, String ip, Integer port){
		this.userId = userId;
		this.firstName = firstName;
		this.lastName = lastName;
		this.ip = ip;
		this.port = port;
		this.friends = new Vector<String>(); // list of user ids
		this.chats = new HashMap<String, Integer>(); // map of key: userid, val: chatNum
		this.posts = new HashMap<Date, String>(); // map of key: time, val: wallPost
		this.sdf = new SimpleDateFormat("yyyy.MM.dd hh.mm.ss");
	}

	// class getters, setters and booleans
	public String getUserId() {
		return userId;
	}

	public void setUserId(String userId) {
		this.userId = userId;
	}

	public String getFirstName() {
		return firstName;
	}

	public void setFirstName(String firstName) {
		this.firstName = firstName;
	}

	public String getLastName() {
		return lastName;
	}

	public void setLastName(String lastName) {
		this.lastName = lastName;
	}

	public String getIp() {
		return ip;
	}

	public void setIp(String ip) {
		this.ip = ip;
	}

	public Integer getPort() {
		return port;
	}

	public void setPort(Integer port) {
		this.port = port;
	}

	public Vector<String> getFriends(){
		return friends;
	}

	public void setFriends(Vector<String> friends){
		this.friends = friends;
	}

	public void setFriend(String friend){
		String[] f = friend.split(" ");
		for(String lad : this.friends){
			if(lad.contains(f[0])){
				this.friends.remove(lad);
			}
		}
		this.friends.add(friend);
	}

	public Boolean isFriend(String friend){
		return this.friends.contains(friend);
	}
	
	public Boolean hasFriend(){
		return !this.friends.isEmpty();
	}

	public Map<String, Integer> getChats(){
		return chats;
	}

	public void setChats(Map<String, Integer> chats){
		this.chats = chats;
	}

	public Integer setChat(String friend){
		if(this.chats.containsKey(friend)){
			this.chats.put(friend, this.chats.get(friend) + 1);	
		}
		else{
			this.chats.put(friend, 1);
		}
		return this.chats.get(friend);
	}

	public Map<Date, String> getPosts(){
		return posts;
	}

	public void setPosts(Map<Date, String> posts){
		this.posts = posts;
	}

	public void setPost(Date time, String post){
		this.posts.put(time, post);
	}
	
	// file import and export
	public void fileImport() throws IOException, ParseException{
		
		// friends
		// clear if the friends vector is not empty
		if(!this.friends.isEmpty()){
			this.friends.clear();
		}
		
		// define the file to read from
		File file1 = new File("data/friends");
		
		// if the file exists import friend data
		if(file1.exists()){
		
			// open the buffer and file
			BufferedReader fin = new BufferedReader(new FileReader(file1));
		
			// loop through each line in the file: userId
			String line;
			while((line = fin.readLine()) != null){
		
				// insert the users id into the vector
				this.friends.add(line);
			}
			
			// close the buffer and file
			fin.close();
		}
		
		// chats
		// clear if the chats map is not empty
		if(!this.chats.isEmpty()){
			this.chats.clear();
		}
		
		// define the file to read from
		File file2 = new File("data/chats");
		
		// if the file exists import chat data
		if(file2.exists()){

			// open the buffer and file
			BufferedReader fin = new BufferedReader(new FileReader(file2));
		
			// loop through each line in the file: userId chatCount
			String line;
			String[] array;
			while((line = fin.readLine()) != null){
	
				// parse the line
				array = line.split(" ");
		
				// add key: userId and val: chatCount, to map
				this.chats.put(array[0], Integer.parseInt(array[1]));
			}
			
			// close the buffer and file
			fin.close();
		}
		
		// posts
		// clear if the posts map is not empty
		if(!this.posts.isEmpty()){
			this.posts.clear();
		}
		
		// define the file to read from
		File file3 = new File("data/posts");
		
		// if the file exists import post data
		if(file3.exists()){

			// open the buffer and file
			BufferedReader fin = new BufferedReader(new FileReader(file3));
		
			// loop through each line in the file: time wallPost
			String[] array;
			String line;
			while((line = fin.readLine()) != null){
	
				// parse the line
				array = line.split(" ");
				Date date = this.sdf.parse(array[0] + " " + array[1]);
				String wallpost = Joiner.on(" ").join(Arrays.copyOfRange(array, 2, array.length));
						
				// add key: time and val: wallPost, to map
				this.posts.put(date, wallpost);
			}
			
			// close the buffer and file
			fin.close();
		}
	}
	
	public void fileExport() throws IOException{
		
		// friends
		// check that the friends vector is not empty
		if(!this.friends.isEmpty()){
		
			// define the file to write to
			File file1 = new File("data/friends");
		
			// create a new file, if it doesn't already exist
			if(!file1.exists()){
				file1.createNewFile();
			}
		
			// open the buffer and file
			BufferedWriter fout = new BufferedWriter(new FileWriter(file1));
		
			// loop through the vector of friends
			for(String friend : this.friends){

				// write the current friend to file
				fout.write(friend + "\n");
			}
		
			// close the buffer and file
			fout.close();
		}
		
		// chats
		// check that the chats map is not empty
		if(!this.chats.isEmpty()){
		
			// define the file to write to
			File file2 = new File("data/chats");
				
			// create a new file, if it doesn't already exist
			if(!file2.exists()){
				file2.createNewFile();
			}
				
			// open the buffer and file
			BufferedWriter fout = new BufferedWriter(new FileWriter(file2));
				
			// loop through the map of chats
			for(Entry<String, Integer> entry : this.chats.entrySet()){
				
				// write the current friend and chat number to file
				fout.write(entry.getKey() + " " + Integer.toString(entry.getValue()) + "\n");
			}
			
			// close the buffer and file
			fout.close();
		}
		
		// posts
		// check that the posts map is not empty
		if(!this.posts.isEmpty()){
		
			// define the file to write to
			File file3 = new File("data/posts");
				
			// create a new file, if it doesn't already exist
			if(!file3.exists()){
				file3.createNewFile();
			}
				
			// open the buffer and file
			BufferedWriter fout = new BufferedWriter(new FileWriter(file3));
				
			// loop through the map of posts
			for(Entry<Date, String> entry : this.posts.entrySet()){
				
				// write the current time and wall post to file
				fout.write(sdf.format(entry.getKey()) + " " + entry.getValue() + "\n");
			}
			
			// close the buffer and file
			fout.close();
		}
	}
}