/*
** Zabbix
** Copyright (C) 2001-2014 Zabbix SIA
**
** This program is free software; you can redistribute it and/or modify
** it under the terms of the GNU General Public License as published by
** the Free Software Foundation; either version 2 of the License, or
** (at your option) any later version.
**
** This program is distributed in the hope that it will be useful,
** but WITHOUT ANY WARRANTY; without even the implied warranty of
** MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
** GNU General Public License for more details.
**
** You should have received a copy of the GNU General Public License
** along with this program; if not, write to the Free Software
** Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
**/

#include "common.h"
#include "sysinfo.h"
#include "../common/common.h"

static struct ifmibdata	ifmd;

static int	get_ifmib_general(const char *if_name)
{
	int	mib[6], ifcount;
	size_t	len;

	mib[0] = CTL_NET;
	mib[1] = PF_LINK;
	mib[2] = NETLINK_GENERIC;
	mib[3] = IFMIB_SYSTEM;
	mib[4] = IFMIB_IFCOUNT;

	len = sizeof(ifcount);

	if (-1 == sysctl(mib, 5, &ifcount, &len, NULL, 0))
		return FAIL;

	mib[3] = IFMIB_IFDATA;
	mib[5] = IFDATA_GENERAL;

	len = sizeof(ifmd);

	for (mib[4] = 1; mib[4] <= ifcount; mib[4]++)
	{
		if (-1 == sysctl(mib, 6, &ifmd, &len, NULL, 0))
		{
			if (ENOENT == errno)
				continue;

			break;
		}

		if (0 == strcmp(ifmd.ifmd_name, if_name))
			return SUCCEED;
	}

	return FAIL;
}

int	NET_IF_IN(const char *cmd, const char *param, unsigned flags, AGENT_RESULT *result)
{
	char	if_name[MAX_STRING_LEN], mode[32];

	if (2 < num_param(param))
		return SYSINFO_RET_FAIL;

	if (0 != get_param(param, 1, if_name, sizeof(if_name)))
		return SYSINFO_RET_FAIL;

	if (0 != get_param(param, 2, mode, sizeof(mode)))
		*mode = '\0';

	if (FAIL == get_ifmib_general(if_name))
		return SYSINFO_RET_FAIL;

	if ('\0' == *mode || 0 == strcmp(mode, "bytes"))	/* default parameter */
		SET_UI64_RESULT(result, ifmd.ifmd_data.ifi_ibytes);
	else if (0 == strcmp(mode, "packets"))
		SET_UI64_RESULT(result, ifmd.ifmd_data.ifi_ipackets);
	else if (0 == strcmp(mode, "errors"))
		SET_UI64_RESULT(result, ifmd.ifmd_data.ifi_ierrors);
	else if (0 == strcmp(mode, "dropped"))
		SET_UI64_RESULT(result, ifmd.ifmd_data.ifi_iqdrops);
	else
		return SYSINFO_RET_FAIL;

	return SYSINFO_RET_OK;
}

int	NET_IF_OUT(const char *cmd, const char *param, unsigned flags, AGENT_RESULT *result)
{
	char	if_name[MAX_STRING_LEN], mode[32];

	if (2 < num_param(param))
		return SYSINFO_RET_FAIL;

	if (0 != get_param(param, 1, if_name, sizeof(if_name)))
		return SYSINFO_RET_FAIL;

	if (0 != get_param(param, 2, mode, sizeof(mode)))
		*mode = '\0';

	if (FAIL == get_ifmib_general(if_name))
		return SYSINFO_RET_FAIL;

	if ('\0' == *mode || 0 == strcmp(mode, "bytes"))	/* default parameter */
		SET_UI64_RESULT(result, ifmd.ifmd_data.ifi_obytes);
	else if (0 == strcmp(mode, "packets"))
		SET_UI64_RESULT(result, ifmd.ifmd_data.ifi_opackets);
	else if (0 == strcmp(mode, "errors"))
		SET_UI64_RESULT(result, ifmd.ifmd_data.ifi_oerrors);
	else
		return SYSINFO_RET_FAIL;

	return SYSINFO_RET_OK;
}

int	NET_IF_TOTAL(const char *cmd, const char *param, unsigned flags, AGENT_RESULT *result)
{
	char	if_name[MAX_STRING_LEN], mode[32];

	if (2 < num_param(param))
		return SYSINFO_RET_FAIL;

	if (0 != get_param(param, 1, if_name, sizeof(if_name)))
		return SYSINFO_RET_FAIL;

	if (0 != get_param(param, 2, mode, sizeof(mode)))
		*mode = '\0';

	if (FAIL == get_ifmib_general(if_name))
		return SYSINFO_RET_FAIL;

	if ('\0' == *mode || 0 == strcmp(mode, "bytes"))	/* default parameter */
		SET_UI64_RESULT(result, (zbx_uint64_t)ifmd.ifmd_data.ifi_ibytes + ifmd.ifmd_data.ifi_obytes);
	else if (0 == strcmp(mode, "packets"))
		SET_UI64_RESULT(result, (zbx_uint64_t)ifmd.ifmd_data.ifi_ipackets + ifmd.ifmd_data.ifi_opackets);
	else if (0 == strcmp(mode, "errors"))
		SET_UI64_RESULT(result, (zbx_uint64_t)ifmd.ifmd_data.ifi_ierrors + ifmd.ifmd_data.ifi_oerrors);
	else
		return SYSINFO_RET_FAIL;

	return SYSINFO_RET_OK;
}

int     NET_TCP_LISTEN(const char *cmd, const char *param, unsigned flags, AGENT_RESULT *result)
{
	char		tmp[8], command[64];
	unsigned short	port;
	int		res;

	if (1 < num_param(param))
		return SYSINFO_RET_FAIL;

	if (0 != get_param(param, 1, tmp, sizeof(tmp)))
		return SYSINFO_RET_FAIL;

	if (FAIL == is_ushort(tmp, &port))
		return SYSINFO_RET_FAIL;

	zbx_snprintf(command, sizeof(command), "netstat -an | grep '^tcp.*\\.%hu[^.].*LISTEN' | wc -l", port);

	if (SYSINFO_RET_FAIL == (res = EXECUTE_INT(NULL, command, flags, result)))
		return res;

	if (1 < result->ui64)
		result->ui64 = 1;

	return res;
}

int     NET_UDP_LISTEN(const char *cmd, const char *param, unsigned flags, AGENT_RESULT *result)
{
	char		tmp[8], command[64];
	unsigned short	port;
	int		res;

	if (1 < num_param(param))
		return SYSINFO_RET_FAIL;

	if (0 != get_param(param, 1, tmp, sizeof(tmp)))
		return SYSINFO_RET_FAIL;

	if (FAIL == is_ushort(tmp, &port))
		return SYSINFO_RET_FAIL;

	zbx_snprintf(command, sizeof(command), "netstat -an | grep '^udp.*\\.%hu[^.].*\\*\\.\\*' | wc -l", port);

	if (SYSINFO_RET_FAIL == (res = EXECUTE_INT(NULL, command, flags, result)))
		return res;

	if (1 < result->ui64)
		result->ui64 = 1;

	return res;
}

int     NET_IF_COLLISIONS(const char *cmd, const char *param, unsigned flags, AGENT_RESULT *result)
{
	char	if_name[MAX_STRING_LEN];

	if (1 < num_param(param))
		return SYSINFO_RET_FAIL;

	if (0 != get_param(param, 1, if_name, sizeof(if_name)))
		return SYSINFO_RET_FAIL;

	if (FAIL == get_ifmib_general(if_name))
		return SYSINFO_RET_FAIL;

	SET_UI64_RESULT(result, ifmd.ifmd_data.ifi_collisions);

	return SYSINFO_RET_OK;
}
