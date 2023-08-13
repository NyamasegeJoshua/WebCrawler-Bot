import streamlit as st
import datetime
import requests
from bs4 import BeautifulSoup
import sqlite3

# Initialize a list to store chat history
chat_history = []

# Connect to SQLite database
conn = sqlite3.connect("chat_history.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS chat_history
             (user_input TEXT, bot_response TEXT)''')
conn.commit()

# Initialize a list to store chat history
chat_history = []

def web_scraping(qs):
    global flag2
    global loading

    URL = 'https://www.google.com/search?q=' + qs
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, 'html.parser')
    
    links = soup.findAll("a")
    all_links = []
    for link in links:
       link_href = link.get('href')
       if "url?q=" in link_href and not "webcache" in link_href:
           all_links.append((link.get('href').split("?q=")[1].split("&sa=U")[0]))
           

    flag= False
    for link in all_links:
       if 'https://en.wikipedia.org/wiki/' in link:
           wiki = link
           flag = True
           break

    div0 = soup.find_all('div',class_="kvKEAb")
    div1 = soup.find_all("div", class_="Ap5OSd")
    div2 = soup.find_all("div", class_="nGphre")
    div3  = soup.find_all("div", class_="BNeawe iBp4i AP7Wnd")

    if len(div0)!=0:
        answer = div0[0].text
    elif len(div1) != 0:
       answer = div1[0].text+"\n"+div1[0].find_next_sibling("div").text
    elif len(div2) != 0:
       answer = div2[0].find_next("span").text+"\n"+div2[0].find_next("div",class_="kCrYT").text
    elif len(div3)!=0:
        answer = div3[1].text
    elif flag==True:
       page2 = requests.get(wiki)
       soup = BeautifulSoup(page2.text, 'html.parser')
       title = soup.select("#firstHeading")[0].text
       
       paragraphs = soup.select("p")
       for para in paragraphs:
           if bool(para.text.strip()):
               answer = title + "\n" + para.text
               break
    else:
        answer = "Sorry. I could not find the desired results"


    return answer

def wishme():
    hour = datetime.datetime.now().hour

    if 0 <= hour < 12:
        text = "Good Morning. I am JoshBot. What can i do for you?"
    elif 12 <= hour < 18:
        text = "Good Afternoon. I am JoshBot. What can i do for you??"
    else:
        text = "Good Evening. I am JoshBot. What can i do for you?"

    return text

def save_to_database(user_input, bot_response):
    c.execute("INSERT INTO chat_history (user_input, bot_response) VALUES (?, ?)", (user_input, bot_response))
    conn.commit()

def main():
    st.title("JoshBot")

    # Add thinking emoji icon
    # st.image("thinking-emoji.png", width=80)

    st.write("Ask Me Anything!")

    # Reload and Quit buttons
    col1, col2 = st.columns(2)
    if col1.button("Reload", key="reload_button"):
        if chat_history:
            last_user_input = chat_history[-2][3:]  # Extract the user input from the history
            response = web_scraping(last_user_input)
            chat_history[-1] = f"JoshBot: {response}"  # Update the last response in chat history
            save_to_database(last_user_input, response)
            st.experimental_rerun()

    if col2.button("Quit", key="quit_button"):
        conn.close()
        st.stop()

    # Display chat history
    st.write("Chat History:")
    for entry in chat_history:
        st.write(entry)

    user_input = st.text_input("Type your message here:")
    if st.button("Send", key="send_button"):
        st.text_area("You:", user_input)

        if user_input.lower() in ["hello", "hi", "hey"]:
            response = wishme()
        else:
            response = web_scraping(user_input)

        # Display bot's response using Markdown formatting
        st.markdown("### JoshBot's response:")
        st.markdown(response)

        # Save to database
        save_to_database(user_input, response)

        # Add user input and bot response to chat history
        chat_history.append(f"You: {user_input}")
        chat_history.append(f"JoshBot: {response}")

if __name__ == "__main__":
    main()