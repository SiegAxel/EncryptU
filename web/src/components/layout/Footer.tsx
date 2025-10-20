// src/components/layout/Footer.tsx
"use client";

import Link from "next/link";
import Container from "@/components/layout/ui/Container";
import SocialBar from "./SocialBar";

export default function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="w-full">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-8 py-10 max-w-xs mx-auto sm:max-w-2xl lg:max-w-full">
                <div className="col-span-full lg:mb-10 max-lg:border-b max-lg:pb-8 lg:border-r border-gray-200 lg:col-span-2 lg:max-w-xs lg:mb-0">
                    <a href="#" className="flex justify-center mb-5 lg:justify-start mr-10">
                        <img src="/negrito.png" alt="" />
                    </a>
                    <ul className="grid gap-5">
                        <li className="flex items-center justify-center gap-2 lg:justify-start">
                            <svg width="20" height="16" viewBox="0 0 20 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M1.87798 3.83594L6.80031 7.08201C8.55849 8.13692 9.43758 8.66437 10.4034 8.64139C11.3693 8.6184 12.2223 8.04973 13.9283 6.91239L18.1246 3.83594M8.33464 14.6693H11.668C14.8107 14.6693 16.382 14.6693 17.3583 13.693C18.3346 12.7166 18.3346 11.1453 18.3346 8.0026C18.3346 4.85991 18.3346 3.28856 17.3583 2.31225C16.382 1.33594 14.8107 1.33594 11.668 1.33594H8.33464C5.19194 1.33594 3.62059 1.33594 2.64428 2.31225C1.66797 3.28856 1.66797 4.85991 1.66797 8.0026C1.66797 11.1453 1.66797 12.7166 2.64428 13.693C3.62059 14.6693 5.19194 14.6693 8.33464 14.6693Z" stroke="#df1212" strokeWidth="1.6" strokeLinecap="round"/>
                                </svg>
                                Soporte.encryptu@gmail.com    
                        </li>
                        <li className="flex items-center justify-center gap-2 lg:justify-start">
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M15.9655 12.6929C15.672 12.5811 15.5252 12.5251 15.3708 12.5118C15.2164 12.4984 15.0622 12.5283 14.7538 12.5881L12.3984 13.0445C12.0235 13.1172 11.836 13.1535 11.6427 13.1227C11.4493 13.0918 11.2957 13.0064 10.9886 12.8356C9.07557 11.7718 7.78657 10.5439 6.95042 8.81181C6.827 8.55614 6.76529 8.4283 6.74183 8.25256C6.71837 8.07683 6.74863 7.91452 6.80915 7.5899L7.27298 5.1021C7.32932 4.79993 7.35749 4.64884 7.3442 4.49766C7.33092 4.34649 7.27683 4.20263 7.16866 3.91491L6.61323 2.43758C6.35178 1.74217 6.22105 1.39447 5.93618 1.19723C5.65132 1 5.27985 1 4.53692 1H2.68622C1.66783 1 0.866113 1.84144 1.01869 2.8481C1.39788 5.36068 2.51739 9.91727 5.78835 13.1882C9.22363 16.6235 14.172 18.1141 16.895 18.7072C17.9468 18.9357 18.8794 18.1159 18.8794 17.0388V15.3317C18.8794 14.592 18.8794 14.2222 18.6836 13.938C18.4877 13.6538 18.1421 13.5222 17.4509 13.2588L15.9655 12.6929Z" stroke="#df1212" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
                                </svg>
                                +91 945 658 3256
                        </li>
                        <li className="flex items-center justify-center gap-2 lg:justify-start">
                            <svg width="16" height="20" viewBox="0 0 16 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M14.6654 8.60868C14.6654 11.8081 12.1279 14.3862 10.184 16.6526C9.22437 17.7713 8.74457 18.3307 7.9987 18.3307C7.25282 18.3307 6.77302 17.7713 5.81342 16.6526C3.86945 14.3862 1.33203 11.8081 1.33203 8.60868C1.33203 6.76685 2.03441 5.00046 3.28465 3.69809C4.5349 2.39573 6.23059 1.66406 7.9987 1.66406C9.76681 1.66406 11.4625 2.39573 12.7127 3.69809C13.963 5.00046 14.6654 6.76685 14.6654 8.60868Z" stroke="#df1212ff" strokeWidth="1.6"/>
                                <path d="M9.66536 7.7406C9.66536 8.69945 8.91917 9.47676 7.9987 9.47676C7.07822 9.47676 6.33203 8.69945 6.33203 7.7406C6.33203 6.78175 7.07822 6.00445 7.9987 6.00445C8.91917 6.00445 9.66536 6.78175 9.66536 7.7406Z" stroke="#df1212ff" strokeWidth="1.6"/>
                                </svg>
                                Av. San Carlos 1340, Puente Alto
                        </li>
                        <SocialBar />
                    </ul>
                </div>
                
                <div className="lg:mx-auto text-left ">
                    <h4 className="text-lg text-gray-900 font-medium mb-7">Pagedone</h4>
                    <ul className="text-sm  transition-all duration-500">
                        <li className="mb-6"><a href="javascript:;"  className="text-gray-600 hover:text-gray-900">Home</a></li>
                        <li className="mb-6"><a href="javascript:;"  className=" text-gray-600 hover:text-gray-900">About</a></li>
                        <li><a href="javascript:;"  className=" text-gray-600 hover:text-gray-900">Pricing</a></li>
                    </ul>
                </div>
                <div className="lg:mx-auto text-left">
                    <h4 className="text-lg text-gray-900 font-medium mb-7">Products</h4>
                    <ul className="text-sm  transition-all duration-500">
                        <li className="mb-6"><a href="javascript:;"  className="text-gray-600 hover:text-gray-900">Figma UI System</a></li>
                        <li className="mb-6"><a href="javascript:;"  className=" text-gray-600 hover:text-gray-900">Icons Assets</a></li>
                        <li><a href="javascript:;"  className=" text-gray-600 hover:text-gray-900">Responsive Blocks</a></li>
                    </ul>
                </div>
                <div className="lg:mx-auto text-left ">
                    <h4 className="text-lg text-gray-900 font-medium mb-7">Resources</h4>
                    <ul className="text-sm  transition-all duration-500">
                        <li className="mb-6"><a href="javascript:;"  className="text-gray-600 hover:text-gray-900">FAQs</a></li>
                        <li className="mb-6"><a href="javascript:;"  className=" text-gray-600 hover:text-gray-900">Quick Start</a></li>
                        <li ><a href="javascript:;"  className=" text-gray-600 hover:text-gray-900">Documentation</a></li>
                    </ul>
                </div>
                <div className="lg:mx-auto text-left ">
                    <h4 className="text-lg text-gray-900 font-medium mb-7">Support</h4>
                    <ul className="text-sm  transition-all duration-500">
                        <li className="mb-6"><a href="javascript:;"  className="text-gray-600 hover:text-gray-900">Customer Support</a></li>
                        <li className="mb-6"><a href="javascript:;"  className=" text-gray-600 hover:text-gray-900">License</a></li>
                        <li ><a href="javascript:;"  className=" text-gray-600 hover:text-gray-900">Terms & Conditions</a></li>
                    </ul>
                </div>
            </div>
            
            <div className="py-7 border-t border-gray-200">
                <div className="flex items-center justify-center ">
                    <span className="text-sm text-gray-500 ">©<a href="#">EncryptU</a> 2025, All rights reserved.</span>
                </div>
            </div>
        </div>
    </footer>
  );
}
