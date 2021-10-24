import * as React from 'react'
import PropTypes from 'prop-types'
import { BrowserRouter, Link as BrowserLink } from 'react-router-dom'

import Box from '@mui/material/Box'
import Container from '@mui/material/Container'
import CssBaseline from '@mui/material/CssBaseline'
import Divider from '@mui/material/Divider'
import Icon from '@mui/material/Icon'
import IconButton from '@mui/material/IconButton'
import List from '@mui/material/List'
import ListItem from '@mui/material/ListItem'
import ListItemIcon from '@mui/material/ListItemIcon'
import ListItemText from '@mui/material/ListItemText'
import Toolbar from '@mui/material/Toolbar'
import Tooltip from '@mui/material/Tooltip'
import Typography from '@mui/material/Typography'

import MenuIcon from '@mui/icons-material/Menu'
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft'

import StyledAppBar from './StyledAppBar'
import StyledDrawer from './StyledDrawer'

export default class DashboardRouter extends React.Component {
  state = {
    open: false
  }

  handleToggleDrawer = () => {
    this.setState((state, props) => ({ open: !state.open }))
  }

  render() {
    const { open } = this.state
    const { basename, title, applications, links, routes, appBarItems } =
      this.props

    return (
      <BrowserRouter basename={basename}>
        <Box sx={{ display: 'flex' }}>
          <CssBaseline />

          <StyledAppBar position="absolute" open={open}>
            <Toolbar
              sx={{
                pr: '24px' // keep right padding when drawer closed
              }}
            >
              <IconButton
                edge="start"
                color="inherit"
                aria-label="open drawer"
                onClick={this.handleToggleDrawer}
                sx={{
                  marginRight: '36px',
                  ...(open && { display: 'none' })
                }}
              >
                <MenuIcon />
              </IconButton>

              <Typography
                component="h1"
                variant="h6"
                color="inherit"
                noWrap
                sx={{ flexGrow: 1 }}
              >
                {title}
              </Typography>

              {appBarItems && appBarItems}
            </Toolbar>
          </StyledAppBar>

          <StyledDrawer variant="permanent" open={open}>
            <Toolbar
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'flex-end',
                px: [1]
              }}
            >
              <IconButton onClick={this.handleToggleDrawer}>
                <ChevronLeftIcon />
              </IconButton>
            </Toolbar>

            <Divider />

            <List>
              {applications.map(application => (
                <Tooltip
                  placement="right"
                  title={
                    <Typography variant="subtitle2" color="inherit">
                      {application.description}
                    </Typography>
                  }
                  key={application.code}
                >
                  <ListItem button component="a" href={application.url}>
                    <ListItemIcon>
                      <Icon>{application.iconName}</Icon>
                    </ListItemIcon>
                    <ListItemText primary={application.title} />
                  </ListItem>
                </Tooltip>
              ))}
            </List>

            <Divider />

            <List>
              {links.map(link => (
                <Tooltip
                  placement="right"
                  title={
                    <Typography variant="subtitle2" color="inherit">
                      {link.description}
                    </Typography>
                  }
                  key={link.code}
                >
                  <ListItem button component={BrowserLink} to={link.path}>
                    <ListItemIcon>
                      <Icon>{link.iconName}</Icon>
                    </ListItemIcon>
                    <ListItemText sx={{ m: 0, p: 0 }} primary={link.title} />
                  </ListItem>
                </Tooltip>
              ))}
            </List>
          </StyledDrawer>

          <Box
            component="main"
            sx={{
              backgroundColor: theme =>
                theme.palette.mode === 'light'
                  ? theme.palette.grey[100]
                  : theme.palette.grey[900],
              flexGrow: 1,
              height: '100vh',
              overflow: 'auto'
            }}
          >
            <Toolbar />

            <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
              {routes}
            </Container>
          </Box>
        </Box>
      </BrowserRouter>
    )
  }
}

DashboardRouter.propTypes = {
  title: PropTypes.string.isRequired,
  basename: PropTypes.string.isRequired,
  applications: PropTypes.array.isRequired,
  links: PropTypes.array.isRequired,
  routes: PropTypes.node.isRequired,
  appBarItems: PropTypes.node
}
