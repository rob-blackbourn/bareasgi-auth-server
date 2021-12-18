import React from 'react'

import Box from '@mui/material/Box'
import CircularProgress from '@mui/material/CircularProgress'
import List from '@mui/material/List'
import ListItem from '@mui/material/ListItem'
import ListItemText from '@mui/material/ListItemText'
import Typography from '@mui/material/Typography'

import { graphqlObservableStreamClient as graphqlClient } from '@barejs/graphql-observable'

export default class Page2 extends React.Component {
  state = {
    people: [],
    isLoaded: false
  }
  subscription = null

  componentDidMount() {
    const { protocol, host} = window.location
    const url = new URL('/example/api/graphql', `${protocol}//${host}`)
    const init = {
      redirect: 'manual',
    }
    const query = `
      query {
        people {
          firstName
          lastName
        }
      }
    `
    const variables = {}
    const operation = null
    this.subscription = graphqlClient(
      url,
      init,
      query,
      variables,
      operation
    )
    .subscribe({
      next: response => {
        if (response.data.people) {
          console.log(response)
          this.setState({
            isLoaded: true,
            people: response.data.people
          })
        }
      },
      complete: () => {
        console.log("Completed")
      },
      error: error => {
        console.error(error.response)
        if (error.response.status === 401 || error.response.type === 'opaqueredirect') {
          this.props.authRedirect()
        }
      }
    })
  }

  componentWillUnmount() {
    if (this.subscription != null) {
      this.subscription.unsubscribe()
    }
  }

  render() {
    const { isLoaded, people } = this.state

    return (
      <Box>
        <Typography variant="h1">Page Two - GraphQL</Typography>

        {!isLoaded ? <CircularProgress/> : (
          <List>
            {people.map(person => (
              <ListItem key={`${person.lastName}.${person.firstName}`}>
                <ListItemText primary={person.lastName} secondary={person.firstName} />
              </ListItem>
            ))}
          </List>
        )}
      </Box>
    )
  }
}
