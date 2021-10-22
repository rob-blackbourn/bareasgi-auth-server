import React from 'react'
import { Route } from 'react-router-dom'
import DashboardRouter from './components/DashboardRouter'
import Page1 from './components/Page1'
import Page2 from './components/Page2'
import Page3 from './components/Page3'

const APPLICATIONS = [
  {
    code: 'dashboard',
    title: 'Dashboard',
    description: 'A dashboard',
    url: '/example/ui',
    iconName: 'dashboard'
  },
  {
    code: 'orders',
    title: 'Orders',
    description: 'The customer orders',
    url: '/orders/ui',
    iconName: 'shopping_cart'
  },
  {
    code: 'customers',
    title: 'Customers',
    description: 'Our customers',
    url: '/customers/ui',
    iconName: 'people'
  },
  {
    code: 'reports',
    title: 'Reports',
    description: 'A collection of reports',
    url: '/reports/ui',
    iconName: 'bar_chart'
  },
  {
    code: 'integrations',
    title: 'Integrations',
    description: 'Other integrations',
    url: '/integrations/ui',
    iconName: 'list_item'
  }
]

const LINKS = [
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
    iconName: 'shopping_cart'
  },
  {
    code: 'page3',
    title: 'Third Page',
    description: 'The third page',
    path: '/third-page',
    iconName: 'shopping_cart'
  }
]

function AuthenticatedApp() {
  return (
    <DashboardRouter
      title="Example Dashboard"
      basename="/example/ui"
      applications={APPLICATIONS}
      links={LINKS}
      routes={
        <>
          <Route exact path="/" component={Page1} />
          <Route exact path="/first-page" component={Page1} />
          <Route exact path="/second-page" component={Page2} />
          <Route exact path="/third-page" component={Page3} />
        </>
      }
    />
  )
}

export default AuthenticatedApp
