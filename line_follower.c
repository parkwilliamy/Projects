//Run mode is when the robot is following the track
//Calibrate mode is when the robot spins in place for 5s to collect IR sensor readings and normalize them to account for variability between the five sensors
//Run mode is triggered when the pushbutton is pressed for less than half a second, while calibrate mode is triggered if the pushbutton is held down for longer than half a second

#include "main.h"
#include "stdio.h"
#include <math.h>
#include <stdbool.h>
ADC_HandleTypeDef hadc1;
DMA_HandleTypeDef hdma_adc1;
TIM_HandleTypeDef htim2;
TIM_HandleTypeDef htim3;

uint32_t adcValues[5] = {0,0,0,0,0}; //stores adc readings from IR sensors
float normadcValues[5] = {0,0,0,0,0}; //stores normalized adc readings (min/max normalization)
uint32_t min[5] = {4095,4095,4095,4095,4095}; //stores minimum adc readings over most recent calibration period
uint32_t max[5] = {0,0,0,0,0}; //stores maximum adc readings over most recent calibration period

bool running = false; //run state
bool calibrating = false; //calibrate state

uint32_t time_held = 0; //length of time pushbutton is held down
uint32_t start_time = 0;
uint32_t duration = 5000; //calibration period duration (i.e., how long the robot spins for)
//Gains for PID
float Kp = 1;
float Ki = 0;
float Kd = 0.7;
//PID variables
float error = 0; //positive error means right of line, negative means left of line
float prev_error = 0; //used to find error differential between iterations of loop
float integral = 0; //summation of the error over time
float derivative = 0; //difference between error and prev_error
float pid_output = 0;
//PWM values for motors
uint32_t base_speed = 500;
uint32_t left_speed = 0;
uint32_t right_speed = 0;

void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_DMA_Init(void);
static void MX_ADC1_Init(void); //ADC1 has 5 channels to read the 5 IR sensors' values
static void MX_TIM2_Init(void); //TIM2 generates PWM to control right motor
static void MX_TIM3_Init(void); //TIM3 generates PWM to control left motor
void NormalizeSensors(void); //normalizes IR sensor values
void ComputePID(void); //computes the error and speed correction for the motors
void SetMotorSpeed(uint32_t left_speed, uint32_t right_speed); //changes PWM duty cycle to change speed

int main(void)
{

  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();
  MX_DMA_Init();
  MX_ADC1_Init();
  MX_TIM2_Init();
  MX_TIM3_Init();
  HAL_ADC_Start_DMA(&hadc1, adcValues, 5); //starts ADC to read IR sensor values into a buffer
  //Next four lines set motor polarities and configure timers to generate PWM for the L298N driver
  HAL_GPIO_WritePin(GPIOB, GPIO_PIN_13, GPIO_PIN_SET); 
  HAL_GPIO_WritePin(GPIOB, GPIO_PIN_14, GPIO_PIN_SET);
  HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_1);
  HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);
  
  while (1)
  {

	  if (HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_15) == GPIO_PIN_SET && !running && !calibrating) { //if pushbutton is pressed and robot is not running or calibrating

		  start_time = HAL_GetTick();

		  while (HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_15) == GPIO_PIN_SET) {
			  HAL_Delay(50); //debounce delay
		  }

		  time_held = HAL_GetTick() - start_time;

		  if (time_held < 500) running = true; //if pushbutton pressed for less than half a second, run mode activates
		  else calibrating = true; //otherwise, robot will enter calibrate mode

	  }

	  if (running) {

		  NormalizeSensors();
		  ComputePID();

		  //Robot will stop if it detects horizontal line
		  if (normadcValues[0] > 0.6 && normadcValues[1] > 0.6 && normadcValues[3] > 0.6 && normadcValues[4] > 0.6) { //if robot detects horizontal line (sensors detect 60% of the maximum darkness read)

			  running = false;
			  left_speed = 0;
			  right_speed = 0;

		  }

		  //Robot will sharply turn based on the sign of the error before the sensors lost the line
		  else if (normadcValues[0] < 0.3 && normadcValues[1] < 0.3 && normadcValues[2] < 0.3 && normadcValues[3] < 0.3 && normadcValues[4] < 0.3) { //if robot is off the track

		  	  if (prev_error > 0) left_speed = 0;
		  	  else right_speed = 0;

		  	  SetMotorSpeed(left_speed, right_speed);

		  	  //While sensors are off the line, continue normalizing the adc values
		  	  while (normadcValues[0] < 0.3 && normadcValues[1] < 0.3 && normadcValues[2] < 0.3 && normadcValues[3] < 0.3 && normadcValues[4] < 0.3) {

		  		NormalizeSensors();
		  		HAL_Delay(5);

		  	  }

		  	  ComputePID(); //updates error after sensors are back on line

		  }

		  SetMotorSpeed(left_speed, right_speed);

	  }

	  if (calibrating) {

		  start_time = HAL_GetTick();

		  //Reverses motor polarity in order for robot to spin in place during calibration
		  HAL_GPIO_WritePin(GPIOB, GPIO_PIN_12, GPIO_PIN_SET);
		  HAL_GPIO_WritePin(GPIOB, GPIO_PIN_13, GPIO_PIN_RESET);
		  SetMotorSpeed(450,450);

		  while (HAL_GetTick() - start_time < duration) { //sets the calibration period for 5s

			  for (unsigned int i = 0; i < 5; ++i) {
				  if (adcValues[i] < min[i]) min[i] = adcValues[i]; //if new adcval is less than previous min, change min
				  if (adcValues[i] > max[i]) max[i] = adcValues[i]; //same logic as min
			  }

		  }

		  SetMotorSpeed(0,0);

		  //Resets motor polarity back to normal for run mode
		  HAL_GPIO_WritePin(GPIOB, GPIO_PIN_12, GPIO_PIN_RESET);
		  HAL_GPIO_WritePin(GPIOB, GPIO_PIN_13, GPIO_PIN_SET);

		  calibrating = false;

	  }
  }
}

void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
  RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};

  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_NONE;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_HSI;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_0) != HAL_OK)
  {
    Error_Handler();
  }
  PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_ADC;
  PeriphClkInit.AdcClockSelection = RCC_ADCPCLK2_DIV2;
  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
  {
    Error_Handler();
  }
}

static void MX_ADC1_Init(void)
{
  ADC_ChannelConfTypeDef sConfig = {0};
  hadc1.Instance = ADC1;
  hadc1.Init.ScanConvMode = ADC_SCAN_ENABLE;
  hadc1.Init.ContinuousConvMode = ENABLE;
  hadc1.Init.DiscontinuousConvMode = DISABLE;
  hadc1.Init.ExternalTrigConv = ADC_SOFTWARE_START;
  hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc1.Init.NbrOfConversion = 5;
  if (HAL_ADC_Init(&hadc1) != HAL_OK)
  {
    Error_Handler();
  }

  sConfig.Channel = ADC_CHANNEL_0;
  sConfig.Rank = ADC_REGULAR_RANK_1;
  sConfig.SamplingTime = ADC_SAMPLETIME_55CYCLES_5;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }

  sConfig.Channel = ADC_CHANNEL_1;
  sConfig.Rank = ADC_REGULAR_RANK_2;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }

  sConfig.Channel = ADC_CHANNEL_2;
  sConfig.Rank = ADC_REGULAR_RANK_3;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }

  sConfig.Channel = ADC_CHANNEL_3;
  sConfig.Rank = ADC_REGULAR_RANK_4;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }

  sConfig.Channel = ADC_CHANNEL_4;
  sConfig.Rank = ADC_REGULAR_RANK_5;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }

}

static void MX_TIM2_Init(void)
{

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};
  TIM_OC_InitTypeDef sConfigOC = {0};

  htim2.Instance = TIM2;
  htim2.Init.Prescaler = 9;
  htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim2.Init.Period = 799;
  htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
  if (HAL_TIM_Base_Init(&htim2) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim2, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_PWM_Init(&htim2) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim2, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigOC.OCMode = TIM_OCMODE_PWM1;
  sConfigOC.Pulse = 0;
  sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
  sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
  if (HAL_TIM_PWM_ConfigChannel(&htim2, &sConfigOC, TIM_CHANNEL_1) != HAL_OK)
  {
    Error_Handler();
  }

  HAL_TIM_MspPostInit(&htim2);

}

static void MX_TIM3_Init(void)
{

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};
  TIM_OC_InitTypeDef sConfigOC = {0};

  htim3.Instance = TIM3;
  htim3.Init.Prescaler = 9;
  htim3.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim3.Init.Period = 799;
  htim3.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim3.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
  if (HAL_TIM_Base_Init(&htim3) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim3, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_PWM_Init(&htim3) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim3, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigOC.OCMode = TIM_OCMODE_PWM1;
  sConfigOC.Pulse = 0;
  sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
  sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
  if (HAL_TIM_PWM_ConfigChannel(&htim3, &sConfigOC, TIM_CHANNEL_1) != HAL_OK)
  {
    Error_Handler();
  }

  HAL_TIM_MspPostInit(&htim3);

}

static void MX_DMA_Init(void)
{

  __HAL_RCC_DMA1_CLK_ENABLE();
  HAL_NVIC_SetPriority(DMA1_Channel1_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(DMA1_Channel1_IRQn);

}

static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};

  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

  HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13|GPIO_PIN_14|GPIO_PIN_15, GPIO_PIN_RESET);
  HAL_GPIO_WritePin(GPIOB, GPIO_PIN_12|GPIO_PIN_13|GPIO_PIN_14|GPIO_PIN_15, GPIO_PIN_RESET);

  /*Configure GPIO pin : PC13 */
  GPIO_InitStruct.Pin = GPIO_PIN_13;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

  /*Configure GPIO pins : PC14 PC15 */
  GPIO_InitStruct.Pin = GPIO_PIN_14|GPIO_PIN_15;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_PULLDOWN;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

  /*Configure GPIO pins : PB12 PB13 PB14 PB15 */
  GPIO_InitStruct.Pin = GPIO_PIN_12|GPIO_PIN_13|GPIO_PIN_14|GPIO_PIN_15;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

}

void NormalizeSensors(void) {

	for (unsigned int i = 0; i < 5; ++i) {

		normadcValues[i] = (float)(adcValues[i]-min[i])/(max[i]-min[i]); //(raw-min)/(max-min)

	}

}
void ComputePID(void) {

	//Error is computed using weighted average, with -2 given to the rightmost sensor and +2 given to the leftmost sensor
	float num = -2*normadcValues[0]-normadcValues[1]+normadcValues[3]+2*normadcValues[4];
	float denom = normadcValues[0] + normadcValues[1] + normadcValues[2] + normadcValues[3] + normadcValues[4];
	if (denom != 0) error = num/denom * 100; //scales up error to fit more with the scale of motor speed values
	else error = 0;

	integral+=error;
	derivative = error-prev_error;
	//Limit the integral term
	if (integral > 500) integral = 500;
	if (integral < -500) integral = -500;

	//PID algorithm
	pid_output = Kp*error + Ki*integral + Kd*derivative;
	//Robot uses differential motor drive to turn
	left_speed = base_speed - pid_output;
	right_speed = base_speed + pid_output;

	//Limits speed so duty cycle is always between 0 and 100
	if (left_speed > 799) left_speed = 799;
	if (left_speed < 0) left_speed = 0;
	if (right_speed > 799) right_speed = 799;
	if (right_speed < 0) right_speed = 0;

	prev_error = error;

}
void SetMotorSpeed(uint32_t left_speed, uint32_t right_speed) {

	__HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, left_speed);  // Left motor
	__HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, right_speed);  // Right motor

}

void Error_Handler(void)
{
  __disable_irq();
  while (1)
  {
  }
}

#ifdef  USE_FULL_ASSERT

void assert_failed(uint8_t *file, uint32_t line)
{

}
#endif
