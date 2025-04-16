//The python script runs the MediaPipe hand landmark detection model to determine the positions of each finger based on webcam data
//The python script then sends this data to the STM32 through a USB to serial cable (UART)
//Once the STM32 receives this data, the microcontroller sends this data to the servo driver over I2C

#![no_std]
#![no_main]

use cortex_m_rt::entry;
use panic_halt as _;
use core::ptr;

//Flash peripheral registers
const FLASH_ACR: *mut u32 = 0x40022000 as *mut u32;

//RCC peripheral registers
const RCC_CR: *mut u32 = 0x40021000 as *mut u32;
const RCC_CFGR: *mut u32 = 0x40021004 as *mut u32;
const RCC_APB1ENR: *mut u32 = 0x4002101C as *mut u32;
const RCC_APB2ENR: *mut u32 = 0x40021018 as *mut u32;

//GPIO peripheral registers
const GPIOA_CRH: *mut u32 = 0x40010804 as *mut u32;
const GPIOB_CRL: *mut u32 = 0x40010C00 as *mut u32;

//I2C peripheral registers
const I2C_CR1: *mut u32 = 0x40005400 as *mut u32;
const I2C_CR2: *mut u32 = 0x40005404 as *mut u32;
const I2C_DR: *mut u32 = 0x40005410 as *mut u32;
const I2C_CCR: *mut u32 = 0x4000541C as *mut u32;
const I2C_TRISE: *mut u32 = 0x40005420 as *mut u32;
const I2C_SR1: *mut u32 = 0x40005414 as *mut u32;
const I2C_SR2: *mut u32 = 0x40005418 as *mut u32;

//UART peripheral registers
const USART1_SR: *mut u32 = 0x40013800 as *mut u32;
const USART1_DR: *mut u32 = 0x40013804 as *mut u32;
const USART1_CR1: *mut u32 = 0x4001380C as *mut u32;
const USART1_BRR: *mut u32 = 0x40013808 as *mut u32;

//PCA9685 registers
const PRE_SCALE: u32 = 0xFE as u32;
const MODE1: u32 = 0x00 as u32;
const MODE2: u32 = 0x01 as u32;
const ON_L0: u32 = 0x6 as u32;

#[entry]
fn main() -> ! {

    SysClockConfig();
    I2C1_Config();
    USART1_Config();

    I2C_Transmit_Single(MODE1, 1<<4); //turn PCA9685 sleep mode on
    I2C_Transmit_Single(MODE2, 0x04); //default settings
    I2C_Transmit_Single(PRE_SCALE, 121);
    I2C_Transmit_Single(MODE1, 1<<5); //turn sleep mode off and auto-increment on

    loop {

        let pulse_widths = USART1_GetArray(); //receives array of pulse widths over UART from python script
        I2C_Transmit_Multi(ON_L0, &pulse_widths); //passes pwm values to servos

    }
}

fn SysClockConfig() {

    unsafe {

        let mut cr = core::ptr::read_volatile(RCC_CR);
        cr |= 1<<16; //Enable HSE
        ptr::write_volatile(RCC_CR, cr);
        while (core::ptr::read_volatile(RCC_CR) & (1<<17)) == 0 {} //Wait for HSE to be ready

        ptr::write_volatile(RCC_APB1ENR, 1<<28); //Enable PWREN

        let mut acr = core::ptr::read_volatile(FLASH_ACR);
        acr |= 1 << 4; //Set prefetch buffer
        core::ptr::write_volatile(FLASH_ACR, acr);
        while (core::ptr::read_volatile(FLASH_ACR) & (1<<5)) == 0 {} //Wait for prefetch buffer to be ready
        acr |= 0b010 << 0; //Set latency to 2 wait states
        core::ptr::write_volatile(FLASH_ACR, acr);

        let mut cfgr = core::ptr::read_volatile(RCC_CFGR);
        cfgr |= 0b0000 << 4; //Set AHB prescaler to 1
        cfgr |= 0b100 << 8; //Set APB1 prescaler to 2
        cfgr |= 0b000 << 11; //Set APB2 prescaler to 1
        cfgr |= 0b0111 << 18; //Set PLLMUL to 9 to set system clock to 72MHz
        cfgr |= 1 << 16; //Set PLLSRC to HSE
        cfgr |= 0 << 17; //Set PREDIV1 to 1
        core::ptr::write_volatile(RCC_CFGR, cfgr);

        cr |= 1<<24; //Enable PLL
        core::ptr::write_volatile(RCC_CR, cr);
        while (core::ptr::read_volatile(RCC_CR) & (1<<25)) == 0 {} //Wait for PLL to be ready
        
        cfgr |= 10; //Set PLL as system clock
        core::ptr::write_volatile(RCC_CFGR, cfgr);
        while (core::ptr::read_volatile(RCC_CFGR) & (1<<3)) == 0 {} //Wait for PLL to be system clock
        
    }   
}

fn I2C1_Config() {

    unsafe {

        let mut apb1 = core::ptr::read_volatile(RCC_APB1ENR);
        apb1 |= 1<<21; //Enable I2C1 clock
        core::ptr::write_volatile(RCC_APB1ENR, apb1);
        let mut apb2 = core::ptr::read_volatile(RCC_APB2ENR);
        apb2 |= 1<<3; //Enable GPIOB clock
        core::ptr::write_volatile(RCC_APB2ENR, apb2);
        let mut gpiob = core::ptr::read_volatile(GPIOB_CRL);
        gpiob |= 0b11011101<<24; //Set PB6 and PB7 to alternate function open drain
        ptr::write_volatile(GPIOB_CRL, gpiob); //Set PB6 and PB7 for I2C

        let mut cr1 = core::ptr::read_volatile(I2C_CR1);
        cr1 |= 1<<15; //Reset I2C
        core::ptr::write_volatile(I2C_CR1, cr1);
        cr1 &= !(1<<15); //Clear reset
        core::ptr::write_volatile(I2C_CR1, cr1);

        ptr::write_volatile(I2C_CR2, 36); //Set PCLK1 to 30MHz
        ptr::write_volatile(I2C_CCR, 0x801E); //Set SCL to 400kHz with 2:1 duty cycle
        ptr::write_volatile(I2C_TRISE, 11); 
        ptr::write_volatile(I2C_CR1, 1); //Set PE

    }
}

fn I2C1_Start() {

    unsafe {
        
        let mut read = core::ptr::read_volatile(I2C_CR1); //Read CR1 register
        read |= 1 << 10; // Set ACK bit
        ptr::write_volatile(I2C_CR1, read); 
        read |= 1 << 8; // Set START bit
        ptr::write_volatile(I2C_CR1, read); 

        while (core::ptr::read_volatile(I2C_SR1) & 1) == 0 {} //Wait for start flag

        ptr::write_volatile(I2C_DR, 0x80); //Write slave (PCA9685) address with R/W bit set to 0
        
        while (core::ptr::read_volatile(I2C_SR1) & (1<<1)) == 0 {} //Wait for address received flag

        //Clear ADDR bit
        core::ptr::read_volatile(I2C_SR1); 
        core::ptr::read_volatile(I2C_SR2);

    }
    
}

fn I2C1_Stop() {

    unsafe {

        let mut read = core::ptr::read_volatile(I2C_CR1);
        read |= 1<<9; //Set STOP bit
        ptr::write_volatile(I2C_CR1, read); 
        while (core::ptr::read_volatile(I2C_SR2) & (1 << 1)) != 0 {}  // Wait for bus not busy

    }

}

fn I2C_Transmit_Single(register: u32, value: u32) {

    I2C1_Start();

    unsafe {

        while (core::ptr::read_volatile(I2C_SR1) & (1 << 7)) == 0 {} //Wait for TXE flag
        ptr::write_volatile(I2C_DR, register); //Send register address
        while (core::ptr::read_volatile(I2C_SR1) & (1 << 2)) == 0 {} //Wait for BTF flag

        while (core::ptr::read_volatile(I2C_SR1) & (1 << 7)) == 0 {} 
        ptr::write_volatile(I2C_DR, value); //Set register to value
        while (core::ptr::read_volatile(I2C_SR1) & (1 << 2)) == 0 {} 

    }

    I2C1_Stop();

}

fn I2C_Transmit_Multi(register: u32, values: &[u32]) {

    I2C1_Start();

    unsafe {

        ptr::write_volatile(I2C_DR, register); //Send register address

        for value in values {

            while (core::ptr::read_volatile(I2C_SR1) & (1 << 7)) == 0 {} //Wait for data to be sent
            ptr::write_volatile(I2C_DR, 0); //Set ON_L
            while (core::ptr::read_volatile(I2C_SR1) & (1 << 2)) == 0 {} //Wait for BTF flag

            while (core::ptr::read_volatile(I2C_SR1) & (1 << 7)) == 0 {} 
            ptr::write_volatile(I2C_DR, 0); //Set ON_H
            while (core::ptr::read_volatile(I2C_SR1) & (1 << 2)) == 0 {} 

            while (core::ptr::read_volatile(I2C_SR1) & (1 << 7)) == 0 {} 
            ptr::write_volatile(I2C_DR, *value & 255); //Set OFF_L
            while (core::ptr::read_volatile(I2C_SR1) & (1 << 2)) == 0 {} 

            while (core::ptr::read_volatile(I2C_SR1) & (1 << 7)) == 0 {}
            ptr::write_volatile(I2C_DR, *value >> 8); //Set OFF_H
            while (core::ptr::read_volatile(I2C_SR1) & (1 << 2)) == 0 {} 

            
        }

    }

    I2C1_Stop();

}

fn USART1_Config() {

    unsafe {

        let mut apb2 = core::ptr::read_volatile(RCC_APB2ENR);
        apb2 |= 1<<2; //Enable GPIOA clock
        apb2 |= 1<<14; //Enable USART1 clock
        core::ptr::write_volatile(RCC_APB2ENR, apb2);
        let mut gpioa = core::ptr::read_volatile(GPIOA_CRH);
        core::ptr::write_volatile(GPIOA_CRH, 0x44444444); //Reset GPIOA_CRH
        gpioa |= 0b01001010 << 4; //Set PA9 to alternate function push-pull and PA10 to floating input
        core::ptr::write_volatile(GPIOA_CRH, gpioa);
        let mut usart1_cr = core::ptr::read_volatile(USART1_CR1);
        core::ptr::write_volatile(USART1_CR1, 0);
        usart1_cr |= 1<<13; //Enable USART
        core::ptr::write_volatile(USART1_CR1, usart1_cr);
        let mut usart1_brr = core::ptr::read_volatile(USART1_BRR);
        usart1_brr = 0x271; //Set baud rate to 115200
        core::ptr::write_volatile(USART1_BRR, usart1_brr); //Set baud rate to 115200
        usart1_cr |= 1<<2; //Enable receiver
        usart1_cr |= 1<<3; //Enable transmitter
        core::ptr::write_volatile(USART1_CR1, usart1_cr);

    }

}

fn USART1_GetByte() -> u8 {

    unsafe {
       
        while (core::ptr::read_volatile(USART1_SR) & 1<<5) == 0 {} //Wait for RXNE flag
        return core::ptr::read_volatile(USART1_DR) as u8;
        

    }

}

fn USART1_GetArray() -> [u32; 5] {

    while USART1_GetByte() != 100 {} //Wait for start byte to indicate beginning of array
    for _ in 0..3 {
        USART1_GetByte(); //Discard first 3 bytes since data comes in groups of 4 bytes (u32)
    }
    let mut bytes: [u8; 4] = [0, 0, 0, 0];
    let mut array: [u32; 5] = [0, 0, 0, 0, 0];
    for i in 0..5 {
        for j in 0..4 {
            bytes[j] = USART1_GetByte();
        }
        array[i] = u32::from_le_bytes(bytes);
    }
    return array;

}
