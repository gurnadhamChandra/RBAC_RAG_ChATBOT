import axios from 'axios';

const api=axios.create({
    baseURL:'http://localhost:8000',
    headers:{
        'Content-Type':'application/json',
        
    },
    withCredentials:true

})

export const loginUser=async({username,password}:{username:string,password:string})=>{
    try{
        const response=await api.post('/login',{
            username,
            password
        })
        return response.data
    }catch(error){
        console.error('Login error:', error);
        throw new Error('Network error. Please check your connection.');  

        }
    }

export const registerUser=async({username,password,role}:{username:string,password:string,role:string})=>{
    try{
        const response=await api.post('/register',{
            username,
            password,
            role
        })
        return response.data
    }catch(error){
        console.error('Registration error:', error);
        throw new Error('Network error. Please check your connection.');  
    }
}

export const logoutUser=async({username}:{username:string})=>{
    try{
        const response=await api.post('/logout',{
            username
        })
        return response.data
    }catch(error){
        console.error('Logout error:', error);
        throw new Error('Network error. Please check your connection.');  
    }
}

export const chatData=async({query,role}:{query:string,role:string})=>{
  try{
    const response = await api.post("/rag_chat",{
      query,
      role
    })
    return response.data

  }catch(error){
     console.error('Chat error:', error);
        throw new Error(`Network error. Please check your connection.${error}`);
  }
}