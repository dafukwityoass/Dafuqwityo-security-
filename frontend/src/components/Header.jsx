import React, { useState } from 'react';
import { Button } from './ui/button';
import { 
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from './ui/navigation-menu';
import { Search, Menu, X } from 'lucide-react';
import { navigationItems } from '../data/mockData';

const Header = ({ onLoginClick, onPayBillClick, onTalkClick }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="fixed top-0 w-full z-50 bg-[#1a2f4b] text-white">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <h1 className="text-xl font-bold">Paymentus</h1>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <NavigationMenu>
              <NavigationMenuList className="space-x-6">
                {navigationItems.map((item) => (
                  <NavigationMenuItem key={item.title}>
                    <NavigationMenuTrigger className="text-white hover:text-blue-200 bg-transparent">
                      {item.title}
                    </NavigationMenuTrigger>
                    <NavigationMenuContent>
                      <div className="p-6 w-80">
                        <div className="grid gap-3">
                          {item.items.map((subItem) => (
                            <NavigationMenuLink
                              key={subItem}
                              href="#"
                              className="block p-3 rounded-md hover:bg-gray-50 text-gray-900 transition-colors"
                            >
                              {subItem}
                            </NavigationMenuLink>
                          ))}
                        </div>
                      </div>
                    </NavigationMenuContent>
                  </NavigationMenuItem>
                ))}
              </NavigationMenuList>
            </NavigationMenu>
          </div>

          {/* Right Side Actions */}
          <div className="hidden md:flex items-center space-x-4">
            <Button 
              variant="ghost" 
              size="sm"
              className="text-white hover:bg-blue-700"
              onClick={() => console.log('Search clicked')}
            >
              <Search className="h-4 w-4" />
            </Button>
            <Button 
              variant="outline" 
              size="sm"
              className="text-white border-white hover:bg-white hover:text-[#1a2f4b]"
              onClick={onPayBillClick}
            >
              Pay Your Bill
            </Button>
            <Button 
              size="sm"
              className="bg-[#e91e63] hover:bg-[#d81b60] text-white"
              onClick={onTalkClick}
            >
              LET'S TALK
            </Button>
          </div>

          {/* Mobile Menu Button */}
          <Button
            variant="ghost"
            size="sm"
            className="md:hidden text-white"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </Button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-blue-700 py-4">
            <div className="flex flex-col space-y-4">
              {navigationItems.map((item) => (
                <div key={item.title}>
                  <button className="text-white hover:text-blue-200 font-medium">
                    {item.title}
                  </button>
                </div>
              ))}
              <div className="flex flex-col space-y-2 pt-4 border-t border-blue-700">
                <Button 
                  variant="outline" 
                  size="sm"
                  className="text-white border-white hover:bg-white hover:text-[#1a2f4b]"
                  onClick={onPayBillClick}
                >
                  Pay Your Bill
                </Button>
                <Button 
                  size="sm"
                  className="bg-[#e91e63] hover:bg-[#d81b60] text-white"
                  onClick={onTalkClick}
                >
                  LET'S TALK
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;