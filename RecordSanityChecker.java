import java.io.*;

public class RecordSanityChecker {
	public static void main(String[] args) throws IOException {
		try (BufferedReader br = new BufferedReader(new FileReader("StudentScore.txt"))) {
            String text = br.readLine();
            boolean fin = false;
            for (; (text = br.readLine()) != null;) {
            	fin = false;
            	if (text.charAt(0) != 'T' || text.charAt(1) != '0' || text.charAt(2) != '0')
            		fin = true;
            	for (int i = 3; i <= 8; ++i)
            		if (text.charAt(i) > '9' || text.charAt(i) < '0')
            			fin = true;
            	if (text.charAt(9) >= '0' && text.charAt(9) <= '9')
            		fin = true;
            	int now = 9;
            	for (; now < text.length() && (text.charAt(now) > '9' || text.charAt(now) < '0'); ++now)
            		if (text.charAt(now) != ' ' && text.charAt(now) != '	')
            			fin = true;
            	if (now >= text.length())fin = true;
            	String scole = "";
            	for (; now < text.length() && text.charAt(now) >= '0' && text.charAt(now) <= '9'; ++now)
            		scole = scole + text.charAt(now);
            	try {
            		int num = Integer.parseInt(scole);
            		if (num > 100)
            			fin = true;
            	} catch (NumberFormatException nfe) {
            		fin = true;
            	}
            	System.out.print(fin == true ? text + '\n' : "");
            }
            br.close();
        }
	}
}
