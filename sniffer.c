#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <linux/if_ether.h>
#include <net/if.h>
#include <linux/filter.h>
#include <sys/ioctl.h>
#include <string.h>
#include <sys/time.h>
#include <signal.h>
#include <stdbool.h>

/* tamanho máximo de um frame Ethernet*/
#define PCKT_LEN 1518

bool __memcmp(unsigned char *b1, unsigned char *b2, size_t size)
{
	for (size_t i = 0; i < size; i++)
	{
		if (b1[i] != b2[i])
			return false;
	}
	return true;
}

int main(int argc, char **argv)
{
	int fd;
	struct ifreq ethreq;
	int i, size;
	unsigned char buffer[PCKT_LEN];

	/* Cria o Socket Raw */
	if ((fd = socket(PF_PACKET, SOCK_RAW, htons(ETH_P_ALL))) < 0)
	{
		perror("socket:");
		return -1;
	}

	/* Coloca o adaptador de rede em modo promíscuo */
	if (argc > 1)
	{
		strncpy(ethreq.ifr_name, argv[1], IFNAMSIZ);
	}
	else
	{
		strncpy(ethreq.ifr_name, "eth0", IFNAMSIZ);
	}
	if (ioctl(fd, SIOCGIFFLAGS, &ethreq) == -1)
	{
		perror("ioctl");
		close(fd);
		exit(-1);
	}

	ethreq.ifr_flags |= IFF_PROMISC;
	if (ioctl(fd, SIOCSIFFLAGS, &ethreq) == -1)
	{
		perror("ioctl");
		close(fd);
		exit(-1);
	}

	// filter mac addresses
	char source_mac[] = {0x00, 0x00, 0x00, 0xaa, 0x00, 0x01};
	char target_mac[] = {0x00, 0x00, 0x00, 0xaa, 0x00, 0x00};

	while ((size = read(fd, buffer, PCKT_LEN)) > 0)
	{
		/* Exibe tamanho do pacote recebido */
		printf("\n%d:\t", size);

		if ((!__memcmp(source_mac, &buffer[6], 6) &&
			 !__memcmp(source_mac, buffer, 6)) ||
			(!__memcmp(target_mac, &buffer[6], 6) &&
			 !__memcmp(target_mac, buffer, 6)))
		{
			printf("ignoring");
			continue;
		}

		/* exibe os primeiros 14 bytes,  ou seja,
		MAC Address Destino, Mac Address Origem e type do cabeçalho Ethernet */
		printf("target: ");
		for (i = 0; i < 6; i++)
		{
			printf("%02x ", buffer[i]);
		}

		printf(" source: ");
		for (i = 6; i < 12; i++)
		{
			printf("%02x ", buffer[i]);
		}
		printf(" protocol: %04x", (buffer[12] << 8) | buffer[13]);
	}

	return 0;
}
