import React from 'react';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';

import Home from '../../screens/Home';
import Browse from '../../screens/Browse';
import Library from '../../screens/Library';
import Icon from 'react-native-vector-icons/AntDesign';

const Tab = createBottomTabNavigator();

const screenOptions = (route, color) => {
  let iconName;

  switch (route.name) {
    case 'Browse':
      iconName = 'appstore-o';
      break;
    case 'Home':
      iconName = 'home';
      break;
    case 'Library':
      iconName = 'folder1';
      break;
    default:
      break;
  }

  return <Icon name={iconName} color={color} size={24} />;
};

const TabNavigator = () => {
  return (
    <Tab.Navigator
      screenOptions={({route}) => ({
        tabBarIcon: ({color}) => screenOptions(route, color),
      })}>
      <Tab.Screen name="Browse" component={Browse} />
      <Tab.Screen name="Home" component={Home} />
      <Tab.Screen name="Library" component={Library} />
    </Tab.Navigator>
  );
};

export default TabNavigator;
