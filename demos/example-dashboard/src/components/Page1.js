import React from 'react'

export default class Page1 extends React.Component {
  state = {
    isLoaded: false,
    isError: false,
    text: ''
  }

  componentDidMount() {
    this.props.authenticator
      .fetch(`${window.location.origin}/example/api/hello`)
      .then(response => {
        switch (response.status) {
          case 200:
            return response.text()
          default:
            throw Error('request failed')
        }
      })
      .then(text => {
        this.setState({ text, isLoaded: true, isError: false })
        console.log(text)
      })
      .catch(error => {
        this.setState({ text: error, isLoaded: true, isError: true })
      })
  }
  render() {
    const { isLoaded, isError, text } = this.state

    return (
      <div>
        <h2>Page 1</h2>
        <h4>isLoaded</h4>
        <p>{isLoaded ? 'yes' : 'no'}</p>
        <h4>isError</h4>
        <p>{isError ? 'yes' : 'no'}</p>
        <h4>text</h4>
        <p>{text}</p>
      </div>
    )
  }
}
