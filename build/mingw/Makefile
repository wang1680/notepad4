# Main Makefile for notepad4 project
# TODO: remove dependencies on rm, mkdir and which (with del, rmdir, mkdir and where commands).

.PHONY: all

# Default flags for all configurations and architectures

export CPPFLAGS += -D_WINDOWS -DNOMINMAX -DWIN32_LEAN_AND_MEAN -DSTRICT_TYPED_ITEMIDS -DUNICODE -D_UNICODE \
	-DBOOST_REGEX_STANDALONE -DNO_CXX11_REGEX
export CFLAGS += -std=gnu17 -municode -Wall -Wextra -Wshadow -Wimplicit-fallthrough -Wformat=2 -Wundef $(if $(CLANG),-Wcomma,)
export CXXFLAGS += -std=gnu++20 -municode -Wall -Wextra -Wshadow -Wimplicit-fallthrough -Wformat=2 -Wundef $(if $(CLANG),-Wcomma,)
export LDFLAGS += -mwindows -municode
export LDLIBS += -lkernel32 -luser32 -lgdi32 -lcomctl32 -lcomdlg32 -ladvapi32 -lshlwapi \
	-lshell32 -lole32 -loleaut32 -luuid -luxtheme
export RCFLAGS += -DRC_INVOKED -DUNICODE -D_UNICODE

# Target triplet if specified. e.g. x86_64-w64-mingw32 for 64-bit.
ifdef TRIPLET
	export CC := $(TRIPLET)-$(if $(CLANG),clang,gcc)
	export CXX := $(TRIPLET)-$(if $(CLANG),clang++,g++)
	export RC := $(TRIPLET)-windres
	# which and where will print not found message on stderr.
	ifeq (,$(shell which $(RC) 2>/dev/null))
		export RC := windres
	endif
else
	export CC := $(if $(CLANG),clang,gcc)
	export CXX := $(if $(CLANG),clang++,g++)
	export RC := windres
endif
ifdef CLANG
	ifdef LTO
		LLD := 1
	endif
endif

# Detect target architecture
ifndef ARCH
	ARCH := $(shell $(CC) -dumpmachine)
endif
ifeq (x86_64, $(findstring x86_64, $(ARCH)))
	ARCH := x64
else ifeq (i686, $(findstring i686, $(ARCH)))
	ARCH := Win32
else ifeq (aarch64, $(findstring aarch64, $(ARCH)))
	ARCH := ARM64
	LLD := 1
endif
ifdef TRIPLET
	# llvm-mingw: TRIPLET-ar
	# mingw-w64: TRIPLET-gcc-ar
	export AR := $(TRIPLET)-$(if $(LLD),ar,gcc-ar)
	ifeq (,$(shell which $(AR) 2>/dev/null))
		export AR := $(if $(LLD),llvm-ar,ar)
	endif
else
	export AR := $(if $(LLD),llvm-ar,ar)
endif

# Check build configuration
LLDFLAGS = $(if $(LLD),-fuse-ld=lld,)
ifdef DEBUG
	CONFIG := Debug
	export CPPFLAGS += -D_DEBUG
	export CFLAGS += -g -O0 $(LLDFLAGS)
	export CXXFLAGS += -g -O0 $(LLDFLAGS)
	export LDFLAGS += -O0 $(LLDFLAGS)
	export RCFLAGS += -D_DEBUG
else
	CONFIG := Release
	LTOFLAGS = $(if $(LTO),-flto,)
	export CPPFLAGS += -DNDEBUG
	export CFLAGS += -O2 -ffast-math -fomit-frame-pointer $(LTOFLAGS) $(LLDFLAGS)
	export CXXFLAGS += -O2 -ffast-math -fno-rtti -fomit-frame-pointer $(LTOFLAGS) $(LLDFLAGS)
	export LDFLAGS += -s -O2 -static -Wl,--gc-sections -ffast-math -fno-rtti -fomit-frame-pointer $(LTOFLAGS) $(LLDFLAGS)
endif

# llvm-mingw uses libc++, which requires Windows 7+.
ifeq ($(ARCH), x64)
	export RCFLAGS += -D_WIN64
	ifdef WIN7
		export CPPFLAGS += -D_WIN64 -D_WIN32_WINNT=0x0601 -DWINVER=0x0601
		export LDFLAGS += -Wl,--major-os-version,6 -Wl,--minor-os-version,1
		ifndef LLD
			export LDFLAGS += -Wl,--subsystem,windows:6.01
		endif
	else
		# Windows Vista, Windows Server 2008
		export CPPFLAGS += -D_WIN64 -D_WIN32_WINNT=0x0600 -DWINVER=0x0600
		export LDFLAGS += -Wl,--major-os-version,6 -Wl,--minor-os-version,0
		ifndef LLD
			export LDFLAGS += -Wl,--subsystem,windows:6.00
		endif
	endif
else ifeq ($(ARCH), AVX2)
	# Windows 7 SP1, Windows Server 2008 R2 SP1, 64-bit only
	export CFLAGS += -march=x86-64-v3
	export CXXFLAGS += -march=x86-64-v3
	export RCFLAGS += -D_WIN64
	export CPPFLAGS += -D_WIN64 -D_WIN32_WINNT=0x0601 -DWINVER=0x0601
	export LDFLAGS += -march=x86-64-v3 -Wl,--major-os-version,6 -Wl,--minor-os-version,1
	ifndef LLD
		export LDFLAGS += -Wl,--subsystem,windows:6.01
	endif
else ifeq ($(ARCH), AVX512)
	# Windows 10, Windows Server 2019, 64-bit only
	export CFLAGS += -march=x86-64-v4
	export CXXFLAGS += -march=x86-64-v4
	export RCFLAGS += -D_WIN64
	export CPPFLAGS += -D_WIN64 -D_WIN32_WINNT=0x0A00 -DWINVER=0x0A00
	export LDFLAGS += -march=x86-64-v4 -Wl,--major-os-version,10 -Wl,--minor-os-version,0
	ifndef LLD
		export LDFLAGS += -Wl,--subsystem,windows:10.00
	endif
else ifeq ($(ARCH), Win32)
	export CFLAGS += -msse2 -mfpmath=sse
	export CXXFLAGS += -msse2 -mfpmath=sse
	export RCFLAGS += -DWIN32
	ifdef WIN7
		export CPPFLAGS += -DWIN32 -D_WIN32_WINNT=0x0601 -DWINVER=0x0601
		export LDFLAGS += -msse2 -mfpmath=sse -Wl,--major-os-version,6 -Wl,--minor-os-version,1
		ifndef LLD
			export LDFLAGS += -Wl,--subsystem,windows:6.01
		endif
	else
		# Windows Vista, Windows Server 2008
		export CPPFLAGS += -DWIN32 -D_WIN32_WINNT=0x0600 -DWINVER=0x0600
		export LDFLAGS += -msse2 -mfpmath=sse -Wl,--major-os-version,6 -Wl,--minor-os-version,0
		ifndef LLD
			export LDFLAGS += -Wl,--subsystem,windows:6.00
		endif
	endif
else ifeq ($(ARCH), ARM64)
	# Windows 10 1709, requires llvm-mingw.
	export CPPFLAGS += -D_WIN64 -D_WIN32_WINNT=0x0A00 -DWINVER=0x0A00
	export RCFLAGS += -D_WIN64
	export LDFLAGS += -Wl,--major-os-version,10 -Wl,--minor-os-version,0
else
	$(error '$(ARCH)' is not supported)
endif

# lld linker doesn't need/support subsystem version.
# see https://github.com/mstorsjo/llvm-mingw/issues/152
ifndef LLD
	export RCFLAGS += -O coff
else
	export RCFLAGS += -O res
	export LDFLAGS += -Wl,--subsystem,windows
endif

# Name root build folder
export BINFOLDER := ../bin/$(if $(CLANG),Clang,)$(CONFIG)_$(ARCH)

all: matepath scintilla notepad4

matepath:
	$(MAKE) -f matepath.mk

scintilla:
	$(MAKE) -f scintilla.mk

notepad4: scintilla
	$(MAKE) -f notepad4.mk

clean:
	$(MAKE) -f matepath.mk clean
	$(MAKE) -f scintilla.mk clean
	$(MAKE) -f notepad4.mk clean
	@$(RM) -rf $(BINFOLDER)/obj
