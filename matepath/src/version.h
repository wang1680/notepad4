/******************************************************************************
*
*
* matepath - The universal Explorer-like Plugin
*
* version.h
*   matepath version information
*
* See Readme.txt for more information about this source code.
* Please send me your comments to this work.
*
* See License.txt for details about distribution and modification.
*
*                                              (c) Florian Balmer 1996-2011
*                                                  florian.balmer@gmail.com
*                                              https://www.flos-freeware.ch
*
*
******************************************************************************/
#pragma once

#include "VersionRev.h"

#define DO_STRINGIFY(x)		TEXT(#x)
#define STRINGIFY(x)		DO_STRINGIFY(x)

#define MY_APPNAME					L"matepath"
#define MY_APPNAME_DESCRIPTION		L"matepath File Browser"
#define VERSION_FILEVERSION_NUM		VERSION_MINOR,VERSION_BUILD_NUM,0,VERSION_REV
#define VERSION_FILEVERSION			STRINGIFY(VERSION_MINOR) "." \
									STRINGIFY(VERSION_BUILD) "." STRINGIFY(VERSION_REV)
#define VERSION_LEGALCOPYRIGHT		L"\xA9 2011-2025 Zufu Liu and all contributors"
#define VERSION_COMPANYNAME			L"Zufu Liu et al."
#define VERSION_WEBPAGE_DISPLAY		L"flo's freeware - https://www.flos-freeware.ch"
#define VERSION_EMAIL_DISPLAY		L"florian.balmer@gmail.com"
#define VERSION_NEWPAGE_DISPLAY		L"https://github.com/zufuliu/notepad4"

#define VERSION_BUILD_INFO_FORMAT	L"Compiled on " __DATE__ L" with %s %d.%d.%d."
#if defined(__INTEL_LLVM_COMPILER)
#define VERSION_BUILD_TOOL_NAME		L"Intel oneAPI"
#define VERSION_BUILD_TOOL_MAJOR	(__INTEL_LLVM_COMPILER / 10000)
#define VERSION_BUILD_TOOL_MINOR	((__INTEL_LLVM_COMPILER / 100) % 100)
#define VERSION_BUILD_TOOL_PATCH	(__INTEL_LLVM_COMPILER % 100)
#elif defined(__clang__)
#define VERSION_BUILD_TOOL_NAME		L"Clang"
#define VERSION_BUILD_TOOL_MAJOR	__clang_major__
#define VERSION_BUILD_TOOL_MINOR	__clang_minor__
#define VERSION_BUILD_TOOL_PATCH	__clang_patchlevel__
#elif defined(__GNUC__)
#define VERSION_BUILD_TOOL_NAME		L"GCC"
#define VERSION_BUILD_TOOL_MAJOR	__GNUC__
#define VERSION_BUILD_TOOL_MINOR	__GNUC_MINOR__
#define VERSION_BUILD_TOOL_PATCH	__GNUC_PATCHLEVEL__
#elif defined(__INTEL_COMPILER_BUILD_DATE)
#if defined(__ICL)
#define VERSION_BUILD_TOOL_NAME		L"Intel C++ " STRINGIFY(__ICL)
#else
#define VERSION_BUILD_TOOL_NAME		L"Intel C++"
#endif
#define VERSION_BUILD_TOOL_MAJOR	(__INTEL_COMPILER_BUILD_DATE / 10000)
#define VERSION_BUILD_TOOL_MINOR	((__INTEL_COMPILER_BUILD_DATE / 100) % 100)
#define VERSION_BUILD_TOOL_PATCH	(__INTEL_COMPILER_BUILD_DATE % 100)
#undef VERSION_BUILD_INFO_FORMAT
#define VERSION_BUILD_INFO_FORMAT	L"Compiled on " __DATE__ L" with %s %4d-%02d-%02d."
#elif defined(_MSC_VER)
#define VERSION_BUILD_TOOL_NAME		L"Visual C++"
#define VERSION_BUILD_TOOL_MAJOR	(_MSC_VER / 100) // 2-digit
#define VERSION_BUILD_TOOL_MINOR	(_MSC_VER % 100) // 2-digit
#define VERSION_BUILD_TOOL_PATCH	(_MSC_FULL_VER % 100000) // 5-digit
#define VERSION_BUILD_TOOL_BUILD	_MSC_BUILD // 2?-digit
#undef VERSION_BUILD_INFO_FORMAT
#define VERSION_BUILD_INFO_FORMAT	L"Compiled on " __DATE__ L" with %s %d.%02d.%05d.%d."
#endif

#if defined(_WIN64)
	#if defined(__aarch64__) || defined(_M_ARM64)
		#define VERSION_FILEVERSION_ARCH	L" (arm64) "
	#elif defined(__AVX512F__)
		#define VERSION_FILEVERSION_ARCH	L" (avx512) "
	#elif defined(__AVX2__)
		#define VERSION_FILEVERSION_ARCH	L" (avx2) "
	#else
		#define VERSION_FILEVERSION_ARCH	L" (64-bit) "
	#endif
#else
	#define VERSION_FILEVERSION_ARCH	L" (32-bit) "
#endif
#define VERSION_FILEVERSION_LONG	MY_APPNAME VERSION_FILEVERSION_ARCH \
									STRINGIFY(VERSION_MINOR) L"." STRINGIFY(VERSION_BUILD) \
									L" " VERSION_REV_FULL
