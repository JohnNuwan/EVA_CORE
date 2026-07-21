---
name: "device-drivers"
description: "Développement de drivers — Linux char/mem/block, I2C, SPI, GPIO, kernel modules, DT, device model"
category: "edge-ai"
author: "E.V.A"
version: "1.0.0"
---

# Drivers de Périphériques Embarqués

## Vue d'ensemble

Développement de drivers pour périphériques embarqués : drivers Linux (char, platform, I2C, SPI, GPIO), Device Tree, kernel modules, et drivers bare-metal pour MCU.

## Drivers Linux — Modèle de Périphérique

### Architecture du Device Model

```
┌──────────────────────────────────────────────┐
│                 Userspace                      │
│  open("/dev/mydev")  ioctl()  mmap()  read()  │
└──────────────────────┬───────────────────────┘
                       │ syscall
┌──────────────────────▼───────────────────────┐
│              VFS (Virtual File System)         │
│         inode → file_operations → driver      │
└──────────────────────┬───────────────────────┘
                       │
┌──────────────────────▼───────────────────────┐
│          Device Model (driver core)            │
│  bus → device → driver → probe()/remove()     │
│  Platform Bus / I2C Bus / SPI Bus / USB       │
└──────────────────────┬───────────────────────┘
                       │
┌──────────────────────▼───────────────────────┐
│              Hardware (MMIO, IRQ, DMA)         │
│         ioremap()  request_irq()  dma_alloc()  │
└──────────────────────────────────────────────┘
```

### Kernel Module — Structure de base

```c
// minimal.c — Module noyau minimal
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>

static int __init my_init(void) {
    pr_info("Module chargé\n");
    return 0;
}

static void __exit my_exit(void) {
    pr_info("Module déchargé\n");
}

module_init(my_init);
module_exit(my_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("E.V.A");
MODULE_DESCRIPTION("Driver minimal embarqué");
```

## Driver Char — Périphérique de caractères

### Structure file_operations

```c
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/uaccess.h>  // copy_to_user / copy_from_user
#include <linux/slab.h>     // kmalloc

#define DEVICE_NAME "mydev"
#define CLASS_NAME  "myclass"

static dev_t dev_num;
static struct cdev my_cdev;
static struct class *my_class;

// Buffer interne
#define BUF_SIZE 1024
static char *dev_buf;

// open()
static int my_open(struct inode *inodep, struct file *filep) {
    pr_info("mydev: ouvert\n");
    return 0;
}

// release()
static int my_release(struct inode *inodep, struct file *filep) {
    pr_info("mydev: fermé\n");
    return 0;
}

// read()
static ssize_t my_read(struct file *filep, char __user *buffer,
                       size_t len, loff_t *offset) {
    ssize_t ret;

    if (*offset >= BUF_SIZE) return 0;
    if (len > BUF_SIZE - *offset) len = BUF_SIZE - *offset;

    if (copy_to_user(buffer, dev_buf + *offset, len)) {
        return -EFAULT;
    }

    *offset += len;
    return len;
}

// write()
static ssize_t my_write(struct file *filep, const char __user *buffer,
                        size_t len, loff_t *offset) {
    if (len > BUF_SIZE - *offset) len = BUF_SIZE - *offset;

    if (copy_from_user(dev_buf + *offset, buffer, len)) {
        return -EFAULT;
    }

    *offset += len;
    return len;
}

// ioctl()
static long my_ioctl(struct file *filep, unsigned int cmd,
                     unsigned long arg) {
    switch (cmd) {
        case MY_CMD_RESET:
            memset(dev_buf, 0, BUF_SIZE);
            break;
        case MY_CMD_GET_LEN:
            if (copy_to_user((void __user *)arg, &buf_len, sizeof(buf_len)))
                return -EFAULT;
            break;
        default:
            return -ENOTTY;
    }
    return 0;
}

static struct file_operations fops = {
    .owner   = THIS_MODULE,
    .open    = my_open,
    .release = my_release,
    .read    = my_read,
    .write   = my_write,
    .unlocked_ioctl = my_ioctl,
};

static int __init my_init(void) {
    // Allouer un major/minor dynamique
    if (alloc_chrdev_region(&dev_num, 0, 1, DEVICE_NAME) < 0)
        return -1;

    // Créer cdev
    cdev_init(&my_cdev, &fops);
    if (cdev_add(&my_cdev, dev_num, 1) < 0) {
        unregister_chrdev_region(dev_num, 1);
        return -1;
    }

    // Créer class + device (udev auto-crée /dev/mydev)
    my_class = class_create(THIS_MODULE, CLASS_NAME);
    device_create(my_class, NULL, dev_num, NULL, DEVICE_NAME);

    // Allouer buffer
    dev_buf = kmalloc(BUF_SIZE, GFP_KERNEL);
    memset(dev_buf, 0, BUF_SIZE);

    pr_info("mydev: chargé, major=%d minor=%d\n",
            MAJOR(dev_num), MINOR(dev_num));
    return 0;
}
```

## Driver Platform — Périphérique mémoire-mappé

### Device Tree

```dts
/ {
    my_device: my-device@40005000 {
        compatible = "eva,my-ip-core";
        reg = <0x40005000 0x1000>;
        interrupts = <42 2>;  // IRQ 42, rising edge
        clocks = <&clk 12>;
        reset-gpios = <&gpio3 15 GPIO_ACTIVE_LOW>;
        dmas = <&dma 0 1>;   // DMA channel 0, request 1
        dma-names = "rx";
        status = "okay";
    };
};
```

### Driver Platform

```c
#include <linux/platform_device.h>
#include <linux/of.h>        // Device Tree helpers
#include <linux/of_device.h>
#include <linux/interrupt.h>
#include <linux/io.h>         // ioremap / readl / writel
#include <linux/dmaengine.h>
#include <linux/gpio/consumer.h>
#include <linux/clk.h>

struct my_priv {
    void __iomem *base;
    int irq;
    struct clk *clk;
    struct gpio_desc *reset_gpio;
    struct dma_chan *dma_chan;
    struct device *dev;
    spinlock_t lock;
};

// Probing
static int my_probe(struct platform_device *pdev) {
    struct my_priv *priv;
    struct resource *res;

    priv = devm_kzalloc(&pdev->dev, sizeof(*priv), GFP_KERNEL);
    if (!priv) return -ENOMEM;

    priv->dev = &pdev->dev;
    spin_lock_init(&priv->lock);

    // MMIO
    res = platform_get_resource(pdev, IORESOURCE_MEM, 0);
    priv->base = devm_ioremap_resource(&pdev->dev, res);
    if (IS_ERR(priv->base)) return PTR_ERR(priv->base);

    // IRQ
    priv->irq = platform_get_irq(pdev, 0);
    if (priv->irq < 0) return priv->irq;

    ret = devm_request_irq(&pdev->dev, priv->irq, my_isr,
                            IRQF_TRIGGER_RISING, "mydev", priv);
    if (ret) return ret;

    // Clock
    priv->clk = devm_clk_get(&pdev->dev, NULL);
    if (!IS_ERR(priv->clk)) clk_prepare_enable(priv->clk);

    // GPIO
    priv->reset_gpio = devm_gpiod_get(&pdev->dev, "reset", GPIOD_OUT_HIGH);
    // ... reset sequence

    platform_set_drvdata(pdev, priv);
    dev_info(&pdev->dev, "mydev probé\n");
    return 0;
}

// ISR
static irqreturn_t my_isr(int irq, void *dev_id) {
    struct my_priv *priv = dev_id;
    uint32_t status = readl(priv->base + IRQ_STATUS);

    if (status & RX_READY) {
        uint32_t data = readl(priv->base + RX_DATA);
        // Traiter data — souvent via workqueue
        schedule_work(&priv->work);
    }

    writel(status, priv->base + IRQ_CLEAR);  // Ack
    return IRQ_HANDLED;
}

static const struct of_device_id my_of_match[] = {
    { .compatible = "eva,my-ip-core", },
    { /* sentinel */ }
};
MODULE_DEVICE_TABLE(of, my_of_match);

static struct platform_driver my_driver = {
    .probe  = my_probe,
    .remove = my_remove,
    .driver = {
        .name = "mydev",
        .of_match_table = my_of_match,
    },
};
module_platform_driver(my_driver);
```

## Driver I2C

### Device Tree

```dts
&i2c1 {
    status = "okay";
    clock-frequency = <100000>;  // 100kHz standard

    temperature@48 {
        compatible = "ti,tmp102";
        reg = <0x48>;           // I2C address 7-bit
        #address-cells = <1>;
        #size-cells = <0>;
    };
};
```

### Driver I2C

```c
#include <linux/i2c.h>

struct tmp102_priv {
    struct i2c_client *client;
    int temperature;
    struct mutex lock;
};

static int tmp102_read_temp(struct i2c_client *client, int *temp) {
    u8 reg = 0x00;  // Temperature register
    u8 buf[2];
    struct i2c_msg msgs[2] = {
        { .addr = client->addr, .flags = 0, .len = 1, .buf = &reg },
        { .addr = client->addr, .flags = I2C_M_RD, .len = 2, .buf = buf },
    };
    int ret = i2c_transfer(client->adapter, msgs, 2);
    if (ret != 2) return -EIO;

    // TMP102 : 12-bit signed, 0.0625°C par bit
    s16 raw = (buf[0] << 8) | buf[1];
    *temp = (raw >> 4) * 625 / 10;  // °C × 10
    return 0;
}

static int tmp102_probe(struct i2c_client *client,
                        const struct i2c_device_id *id) {
    struct tmp102_priv *priv = devm_kzalloc(&client->dev, sizeof(*priv), GFP_KERNEL);
    priv->client = client;
    mutex_init(&priv->lock);
    i2c_set_clientdata(client, priv);

    // Config : 12-bit, 4Hz, one-shot (0x60 → 0x00 à 0x01)
    u8 config[] = {0x01, 0x60};  // Register 0x01, Extended mode
    i2c_master_send(client, config, 2);

    dev_info(&client->dev, "TMP102 détecté\n");
    return 0;
}

static const struct i2c_device_id tmp102_id[] = {
    { "tmp102", 0 },
    { }
};
MODULE_DEVICE_TABLE(i2c, tmp102_id);

static const struct of_device_id tmp102_of_match[] = {
    { .compatible = "ti,tmp102" },
    { }
};
MODULE_DEVICE_TABLE(of, tmp102_of_match);

static struct i2c_driver tmp102_driver = {
    .driver = {
        .name = "tmp102",
        .of_match_table = tmp102_of_match,
    },
    .probe    = tmp102_probe,
    .id_table = tmp102_id,
};
module_i2c_driver(tmp102_driver);
```

## Driver SPI

```c
#include <linux/spi/spi.h>

// Device Tree
// &spi1 {
//     status = "okay";
//     cs-gpios = <&gpio3 10 GPIO_ACTIVE_LOW>;
//     adc@0 {
//         compatible = "ti,ads1256";
//         reg = <0>;           // Chip select 0
//         spi-max-frequency = <19200000>;
//     };
// };

static int ads1256_transfer(struct spi_device *spi, u8 *tx, u8 *rx, int len) {
    struct spi_transfer t = {
        .tx_buf = tx,
        .rx_buf = rx,
        .len    = len,
        .cs_change = 0,
        .delay_usecs = 1,
    };
    struct spi_message m;
    spi_message_init(&m);
    spi_message_add_tail(&t, &m);
    return spi_sync(spi, &m);
}

// SPI read via register
int ads1256_reg_read(struct spi_device *spi, u8 reg) {
    u8 tx[3] = {0x0F | (reg << 4), 0, 0};  // RREG command
    u8 rx[3];
    ads1256_transfer(spi, tx, rx, 3);
    return rx[2];
}
```

## DMA Engine

```c
// DMA scatter-gather
struct dma_async_tx_descriptor *tx;
struct dma_slave_config cfg = {
    .direction = DMA_DEV_TO_MEM,
    .src_addr = (phys_addr_t)(priv->base + RX_FIFO),
    .src_addr_width = DMA_SLAVE_BUSWIDTH_4_BYTES,
    .src_maxburst = 4,
    .dst_addr = 0,
    .dst_addr_width = DMA_SLAVE_BUSWIDTH_4_BYTES,
    .dst_maxburst = 4,
};

dmaengine_slave_config(priv->dma_chan, &cfg);

tx = dmaengine_prep_slave_sg(priv->dma_chan, dma_sg, 1,
                              DMA_DEV_TO_MEM, DMA_PREP_INTERRUPT);
tx->callback = dma_callback;
tx->callback_param = priv;
dmaengine_submit(tx);
dma_async_issue_pending(priv->dma_chan);
```

## Driver Bare-Metal (sans OS)

### Pattern HAL (Hardware Abstraction Layer)

```c
// my_periph.h — Interface HAL
typedef struct {
    uint32_t (*init)(void);
    uint32_t (*read)(uint8_t *buf, uint32_t len);
    uint32_t (*write)(const uint8_t *buf, uint32_t len);
    uint32_t (*ioctl)(uint32_t cmd, void *arg);
} my_periph_driver_t;

// my_periph_stm32.c — Implémentation STM32
static uint32_t stm32_init(void) {
    // Activer clock périphérique
    RCC->APB1ENR |= RCC_APB1ENR_USART2EN;
    // Configurer GPIO
    // Configurer USART
    USART2->CR1 = USART_CR1_UE | USART_CR1_TE | USART_CR1_RE;
    return 0;
}

static const my_periph_driver_t stm32_impl = {
    .init  = stm32_init,
    .read  = stm32_usart_read,
    .write = stm32_usart_write,
    .ioctl = stm32_ioctl,
};

// my_periph_imx.c — Implémentation i.MX (même interface)
static const my_periph_driver_t imx_impl = {
    .init  = imx_uart_init,
    .read  = imx_uart_read,
    .write = imx_uart_write,
    .ioctl = imx_ioctl,
};
```

### Polling vs IRQ vs DMA

```c
// Polling — simple, CPU 100%
void wait_for_rx(void) {
    while (!(USART2->SR & USART_SR_RXNE));
    return USART2->DR;
}

// IRQ — efficace, overlap CPU
void USART2_IRQHandler(void) {
    if (USART2->SR & USART_SR_RXNE) {
        uint8_t byte = USART2->DR;
        // Mettre dans ring buffer
        ringbuf_put(&rx_ring, byte);
    }
}

// DMA — zéro CPU, discontinuité mémoire
void DMA_Config(void) {
    // DMA circular buffer UART → RAM
    DMA1_Stream5->CR = DMA_SxCR_CHSEL_4 |    // Ch4=UART2_RX
                       DMA_SxCR_CIRC |        // Circular
                       DMA_SxCR_MINC |        // Memory inc
                       DMA_SxCR_TCIE;         // Transfer complete IRQ
    DMA1_Stream5->NDTR = BUF_SIZE;
    DMA1_Stream5->PAR = (uint32_t)&USART2->DR;
    DMA1_Stream5->M0AR = (uint32_t)uart_rx_buf;
    DMA1_Stream5->CR |= DMA_SxCR_EN;
}
```

## Build et Compilation

### Makefile Module Noyau

```makefile
obj-m += mydriver.o
mydriver-objs := mydriver_main.o mydriver_io.o

KDIR ?= /lib/modules/$(shell uname -r)/build

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean

install:
	insmod mydriver.ko
	rmmod mydriver  # si reload

# Compilation croisée
ARCH ?= arm
CROSS_COMPILE ?= arm-linux-gnueabihf-
KDIR ?= /path/to/kernel/build
```

## Pitfalls

1. **copy_to_user/copy_from_user** : Toujours utiliser dans read/write — jamais memcpy direct
2. **GFP_KERNEL vs GFP_ATOMIC** : GFP_KERNEL peut dormir — pas dans les ISR, utiliser GFP_ATOMIC
3. **Locking** : spin_lock dans ISR, mutex en contexte processus
4. **MMIO** : Toujours utiliser readl/writel (pas dereferencement direct) — garantit les barrières mémoire
5. **Device Tree** : Vérifier les bindings — compatible doit matcher à 100%
6. **Resume** : Vérifier que le driver gère la reprise après suspend (PM ops)
7. **DMA coherent** : Utiliser dma_alloc_coherent ou dma_pool pour les buffers partagés
8. **Module reference** : module_platform_driver() modifie les macros de section

## Ressources

- Linux Device Drivers 3rd Ed. (LDD3) : https://lwn.net/Kernel/LDD3/
- Kernel Documentation : https://www.kernel.org/doc/html/latest/
- Device Tree Specification : https://www.devicetree.org/
- Greg KH — Writing Linux Device Drivers : https://github.com/gregkh/linux