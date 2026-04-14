class node:
    def __init__(self,data):
        self.data=data
        self.next=None
class stack:
    def __init__(self):
        self.head=None
    def push(self,data):
        if self.head==None:
            t=node(data)
            self.head=t
        else:
            t=node(data)
            t.next=self.next
            self.next=t
    def display(self):
        print(self.data)

if __name__=="__main__":
    st=stack()
    st.push(1)
    st.push(1)
    st.push(1)
    st.push(1)
    st.push(1)

    print(st.display())
