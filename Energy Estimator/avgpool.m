function [parameter, MAC] = avgpool(kernel, i, c, strides)
    i = floor((i+1)/strides);
    parameter = c * (kernel * kernel * 1);
    MAC = parameter * i * i;
    parameter = 0;
end

