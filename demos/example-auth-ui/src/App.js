import React, { Component } from 'react'
import SignIn from './components/SignIn'

class App extends Component {
  render() {
    return <SignIn whoamiPath="/auth/api/whoami" loginPath="/auth/api/login" />
  }
}

export default App
