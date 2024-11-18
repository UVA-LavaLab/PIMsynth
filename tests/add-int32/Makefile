# Compiler and flags
CXX = g++
CXXFLAGS = -I$(LIB_PIMEVAL_PATH)/include -I./outputs -I../ # Path to header files
LDFLAGS = -L$(LIB_PIMEVAL_PATH)/lib -l:libpimeval.a # Path to static library and linking

# Target executable
TARGET = test

# Source files 
SRCS = test.cpp

# Object files
OBJS = $(SRCS:.cpp=.o)

# Default target
all: $(TARGET)

# Rule to link the program
$(TARGET): $(OBJS)
	$(CXX) $(OBJS) -o $(TARGET) $(LDFLAGS)

# Rule to compile source files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Clean the build
clean:
	rm -f $(OBJS) $(TARGET)

