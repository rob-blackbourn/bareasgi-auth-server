import React from 'react'
import { Route, Redirect } from 'react-router-dom'
import PropTypes from 'prop-types'

import Typography from '@mui/material/Typography'

import DashboardRouter from '@barejs/dashboard-router'
import { Page1, Page2, Page3 } from './pages'

class Site extends React.Component {
  render() {
    return (
      <DashboardRouter
        title="Example Dashboard"
        basename="/example/ui"
        sites={[
          {
            code: 'app1',
            title: 'Application 1',
            description: 'The first application',
            url: '/example/ui',
            iconName: 'dashboard'
          },
          {
            code: 'app2',
            title: 'Application2',
            description: 'The second application',
            url: '/orders/ui',
            iconName: 'album'
          }
        ]}
        pages={[
          {
            code: 'page1',
            title: 'First Page',
            description: 'The first page',
            path: '/first-page',
            iconName: 'shopping_cart'
          },
          {
            code: 'page2',
            title: 'Second Page',
            description: 'The second page',
            path: '/second-page',
            iconName: 'people'
          },
          {
            code: 'page3',
            title: 'Third Page',
            description: 'The third page',
            path: '/third-page',
            iconName: 'agriculture'
          }
        ]}
        routes={
          <>
            <Redirect exact from="/" to="/first-page" />
            <Route
              exact
              path="/first-page"
              render={props => (
                <Page1 title="hello" {...props} {...this.props} />
              )}
            />
            <Route
              exact
              path="/second-page"
              render={props => <Page2 {...props} {...this.props} />}
            />
            <Route
              exact
              path="/third-page"
              render={props => <Page3 {...props} {...this.props} />}
            />
          </>
        }
        appBarItems={
          <Typography component="h4" variant="subtitle1" color="inherit" noWrap>
            {this.props.authCredentials.sub}
          </Typography>
        }
      />
    )
  }
}

Site.propTypes = {
  authFetch: PropTypes.func.isRequired,
  authCredentials: PropTypes.object.isRequired
}

export default Site
