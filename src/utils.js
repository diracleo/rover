export const isResponseOk = response => {
  if (response.ok) {
    try {
	  return response.json();  
	} catch(ex) {
	  return Promise.reject(new Error('error'));  
    }
  }	else {
    return Promise.reject(new Error('error'));  
  }
}
