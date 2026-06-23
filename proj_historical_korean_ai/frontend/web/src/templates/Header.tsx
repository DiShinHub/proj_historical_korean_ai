import React from 'react';
import { AppBar, Toolbar, Typography, IconButton, Button } from '@mui/material';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import { useTheme } from '../themes/ThemeContext';
import { useRouter } from 'next/router';

const Header: React.FC = () => {
  const { toggleTheme } = useTheme();
  const router = useRouter();

  return (
    <AppBar position="static">
      <Toolbar>

        <Typography
          variant="h6"
          sx={{ cursor: 'pointer', flexGrow: 1 }}
          onClick={() => router.push('/')}
        >
          Historical Korean AI
        </Typography>

        <Button
          color="inherit"
          onClick={() => router.push('/chat')}
        >
          Chat
        </Button>

        <IconButton
          color="inherit"
          onClick={toggleTheme}
        >
          <Brightness4Icon />
        </IconButton>

      </Toolbar>
    </AppBar>
  );
};

export default Header;